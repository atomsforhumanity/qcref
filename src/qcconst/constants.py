"""Physical constants from NIST CODATA 2022 and related sources."""

from __future__ import annotations

import csv
from pathlib import Path

from .collections import NamedCollection, normalize_name
from .models import Value
from .utils import to_table


class ConstantCollection(NamedCollection[Value]):
    @property
    def sources(self) -> list[str]:
        unique_sources = {
            value.source
            for value in self.values()
            if not value.source.startswith("Derived")
        }
        return sorted(unique_sources)

    def show(self) -> None:
        rows = [
            {
                "key": key,
                "name": constant.name,
                "value": float(constant),
                "unit": constant.unit,
                "uncertainty": constant.uncertainty,
                "source": constant.source,
            }
            for key, constant in self.items()
        ]
        to_table(rows)

    def __getattr__(self, name: str) -> Value:
        if name.isupper():
            lowered = normalize_name(name)
            return self[lowered]
        return super().__getattr__(name)


def _load_constants(csv_path: Path) -> ConstantCollection:
    constants_list: list[Value] = []
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            constants_list.append(
                Value(
                    row["value"],
                    row["unit"],
                    row["source"],
                    float(row["uncertainty"]) if row["uncertainty"] else None,
                    row["notes"],
                    name=row["name"],
                )
            )
    return ConstantCollection(
        constants_list,
        source_name=lambda value: value.name,
        canonical_key=lambda value: normalize_name(value.name),
    )


def _load_codata(year: int) -> ConstantCollection:
    codata_path = Path(__file__).parent / "data" / f"codata{year}.csv"
    source = f"CODATA {year}: https://physics.nist.gov/cuu/Constants/Table/allascii.txt"

    def _process_float(value: str) -> float:
        return float(value.replace(" ", "").replace("...", ""))

    constants_list: list[Value] = []
    with codata_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            uncertainty = (
                _process_float(row["uncertainty"])
                if row["uncertainty"] != "(exact)"
                else 0.0
            )
            constants_list.append(
                Value(
                    _process_float(row["value"]),
                    row["unit"],
                    source,
                    uncertainty,
                    "",
                    name=row["quantity"],
                )
            )
    return ConstantCollection(constants_list, source_name=lambda value: value.name)


constants = _load_constants(Path(__file__).parent / "data" / "constants.csv")
codata2022 = _load_codata(2022)
phys = codata2022
constants.codata2022 = codata2022
constants.phys = phys

# Low-cost compatibility shim for legacy uppercase constant access.
for constant in constants.values():
    globals()[constant.name] = constant

__all__ = ["ConstantCollection", "constants", "codata2022", "phys"] + [
    constant.name for constant in constants.values()
]
