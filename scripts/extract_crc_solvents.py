#!/usr/bin/env python3
"""Extract the CRC solvent permittivity table into the package CSV.

This script relies on the `pdftohtml` CLI from poppler because the XML output
preserves the superscript temperature attached to the tabulated dielectric
constant. The generated CSV is written to `src/qcconst/data/solvents/crc.csv`; its
source citation lives in the sibling `crc.meta.json`.
"""

from __future__ import annotations

import csv
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from keys import make_key

ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "CRC Solvent Data.pdf"
OUTPUT_PATH = ROOT / "src" / "qcconst" / "data" / "solvents" / "crc.csv"

NAME_LEFT_MAX = 300
FORMULA_LEFT_MIN = 300
FORMULA_LEFT_MAX = 375
EPSILON_LEFT_MIN = 375
EPSILON_LEFT_MAX = 444
COEFFICIENT_LEFT_MIN = 444
COEFFICIENT_LEFT_MAX = 756
TEMP_RANGE_LEFT_MIN = 756
ROW_ASSIGNMENT_THRESHOLD = 9


@dataclass(frozen=True)
class TextItem:
    top: int
    left: int
    width: int
    font_size: int
    text: str


@dataclass
class ParsedRow:
    name: str
    formula: str | None
    dielectric: float
    dielectric_temperature_k: float | None
    fit_a: float | None
    fit_b: float | None
    fit_c: float | None
    fit_d: float | None
    t_min_k: float | None
    t_max_k: float | None


def load_xml(pdf_path: Path) -> ET.Element:
    result = subprocess.run(
        ["pdftohtml", "-xml", str(pdf_path), "-stdout"],
        check=True,
        capture_output=True,
        text=True,
    )
    return ET.fromstring(result.stdout)


def collect_page_rows(root: ET.Element) -> list[list[TextItem]]:
    rows: list[list[TextItem]] = []
    global_font_sizes = {
        font.attrib["id"]: int(font.attrib["size"])
        for font in root.findall(".//fontspec")
    }

    for page in root.findall("page"):
        items = [
            TextItem(
                top=int(text.attrib["top"]),
                left=int(text.attrib["left"]),
                width=int(text.attrib["width"]),
                font_size=global_font_sizes[text.attrib["font"]],
                text="".join(text.itertext()).strip(),
            )
            for text in page.findall("text")
            if "".join(text.itertext()).strip()
        ]
        header_candidates = [
            item
            for item in items
            if item.text == "Name"
            and abs(item.left - 170) <= 5
            and item.font_size >= 10
        ]
        if not header_candidates:
            continue
        table_top = min(item.top for item in header_candidates) + 10

        base_tops = sorted(
            {
                item.top
                for item in items
                if item.top > table_top
                and item.font_size >= 10
                and item.left < TEMP_RANGE_LEFT_MIN + 40
            }
        )
        page_rows: dict[int, list[TextItem]] = {top: [] for top in base_tops}
        for item in items:
            if item.top <= table_top:
                continue
            matching_tops = [
                top
                for top in base_tops
                if top <= item.top and item.top - top <= ROW_ASSIGNMENT_THRESHOLD
            ]
            if not matching_tops:
                continue
            page_rows[max(matching_tops)].append(item)
        rows.extend(page_rows[top] for top in base_tops if page_rows[top])
    return rows


def join_tokens(items: list[TextItem], *, formula: bool = False) -> str:
    if not items:
        return ""
    items = sorted(items, key=lambda item: (item.left, item.top))
    pieces = [items[0].text]
    previous = items[0]
    for item in items[1:]:
        gap = item.left - (previous.left + previous.width)
        if formula or gap <= 1:
            pieces.append(item.text)
        else:
            pieces.append(f" {item.text}")
        previous = item
    return "".join(pieces).strip()


def parse_coefficients_and_range(
    items: list[TextItem],
) -> tuple[
    tuple[float | None, float | None, float | None, float | None],
    tuple[float | None, float | None],
]:
    tokens: list[str] = []
    for item in sorted(items, key=lambda value: value.left):
        tokens.extend(item.text.split())
    if (
        len(tokens) >= 3
        and re.fullmatch(r"\d+", tokens[-3])
        and tokens[-2] == "-"
        and re.fullmatch(r"\d+", tokens[-1])
    ):
        range_values: tuple[float | None, float | None] = (
            float(tokens[-3]),
            float(tokens[-1]),
        )
        tokens = tokens[:-3]
    else:
        range_values = (None, None)
    values = [float(token) for token in tokens]
    padded = values + [None] * (4 - len(values))
    return (padded[0], padded[1], padded[2], padded[3]), range_values


def parse_dielectric(
    items: list[TextItem], fallback_base: str | None = None
) -> tuple[float, float | None]:
    base = join_tokens([item for item in items if item.font_size >= 10])
    if not base and fallback_base is not None:
        base = fallback_base
    superscript = join_tokens(
        [item for item in items if item.font_size < 10], formula=True
    )
    dielectric = float(base)
    if not superscript:
        return dielectric, None
    return dielectric, round(int(superscript) + 273.15, 2)


def parse_row(items: list[TextItem]) -> ParsedRow | tuple[str, None]:
    name_items = [item for item in items if item.left < NAME_LEFT_MAX]
    formula_items = [
        item for item in items if FORMULA_LEFT_MIN <= item.left < FORMULA_LEFT_MAX
    ]
    epsilon_items = [
        item for item in items if EPSILON_LEFT_MIN <= item.left < EPSILON_LEFT_MAX
    ]
    right_side_items = [item for item in items if item.left >= COEFFICIENT_LEFT_MIN]

    name = join_tokens(name_items)
    if not epsilon_items and not formula_items:
        return name, None

    formula_text = join_tokens(formula_items, formula=True)
    epsilon_fallback: str | None = None
    if not any(item.font_size >= 10 for item in epsilon_items):
        match = re.match(r"^(?P<formula>.*?)(?P<epsilon>\d+\.\d+)$", formula_text)
        if match:
            formula_text = match.group("formula")
            epsilon_fallback = match.group("epsilon")

    dielectric, dielectric_temperature_k = parse_dielectric(
        epsilon_items, fallback_base=epsilon_fallback
    )
    (fit_a, fit_b, fit_c, fit_d), (t_min_k, t_max_k) = parse_coefficients_and_range(
        right_side_items
    )
    return ParsedRow(
        name=name,
        formula=formula_text.strip() or None,
        dielectric=dielectric,
        dielectric_temperature_k=dielectric_temperature_k,
        fit_a=fit_a,
        fit_b=fit_b,
        fit_c=fit_c,
        fit_d=fit_d,
        t_min_k=t_min_k,
        t_max_k=t_max_k,
    )


def merge_continuations(rows: list[list[TextItem]]) -> list[ParsedRow]:
    parsed_rows: list[ParsedRow] = []
    for items in rows:
        parsed = parse_row(items)
        if isinstance(parsed, tuple):
            continuation = parsed[0]
            if parsed_rows:
                parsed_rows[-1].name = f"{parsed_rows[-1].name} {continuation}".strip()
            continue
        parsed_rows.append(parsed)
    return parsed_rows


def assign_keys(rows: list[ParsedRow], output_path: Path) -> dict[str, str]:
    """Keep keys already in the CSV (they may be hand-edited); propose the rest."""
    existing: dict[str, str] = {}
    if output_path.exists():
        with output_path.open(newline="") as f:
            existing = {row["name"]: row["key"] for row in csv.DictReader(f)}
    keys = {row.name: existing.get(row.name) or make_key(row.name) for row in rows}
    duplicates = [key for key, count in Counter(keys.values()).items() if count > 1]
    if duplicates:
        raise ValueError(f"Duplicate keys; edit them by hand: {sorted(duplicates)}")
    return keys


def write_csv(rows: list[ParsedRow], output_path: Path) -> None:
    keys = assign_keys(rows, output_path)
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "key",
                "name",
                "formula",
                "dielectric",
                "dielectric_temperature_k",
                "fit_a",
                "fit_b",
                "fit_c",
                "fit_d",
                "t_min_k",
                "t_max_k",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "key": keys[row.name],
                    "name": row.name,
                    "formula": row.formula or "",
                    "dielectric": row.dielectric,
                    "dielectric_temperature_k": (
                        row.dielectric_temperature_k
                        if row.dielectric_temperature_k is not None
                        else ""
                    ),
                    "fit_a": row.fit_a if row.fit_a is not None else "",
                    "fit_b": row.fit_b if row.fit_b is not None else "",
                    "fit_c": row.fit_c if row.fit_c is not None else "",
                    "fit_d": row.fit_d if row.fit_d is not None else "",
                    "t_min_k": row.t_min_k if row.t_min_k is not None else "",
                    "t_max_k": row.t_max_k if row.t_max_k is not None else "",
                }
            )


def main() -> None:
    xml_root = load_xml(PDF_PATH)
    rows = merge_continuations(collect_page_rows(xml_root))
    write_csv(rows, OUTPUT_PATH)
    print(f"Wrote {len(rows)} solvent rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
