"""Physical constants from NIST CODATA and curated conversion factors.

CODATA releases are discovered from `data/codata/<year>.csv`; `phys` is the latest.
Curated constants in `data/constants/constants.csv` are expressions evaluated
against the latest release, so a new CODATA release updates them automatically.
"""

from __future__ import annotations

from collections import ChainMap
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from .collections import Collection
from .datasets import DATA_DIR, dataset_paths, load_dataset
from .expressions import evaluate
from .models import Value


class ConstantCollection(Collection[Value]):
    codata2022: ConstantCollection
    phys: ConstantCollection

    @property
    def sources(self) -> list[str]:
        return sorted(
            {source for value in self.values() for source in value.source.split("; ")}
        )

    def _row(self, entry: Value) -> dict[str, Any]:
        return {
            "name": entry.name,
            "value": float(entry),
            "unit": entry.unit,
            "uncertainty": entry.uncertainty,
            "source": entry.source,
        }


def _codata_float(value: str) -> float:
    """Handle CODATA's digit-group spaces and ellipses."""
    return float(value.replace(" ", "").replace("...", ""))


def _load_codata() -> dict[int, ConstantCollection]:
    releases = {}
    for path in dataset_paths("codata"):
        dataset = load_dataset(path)
        releases[int(path.stem)] = ConstantCollection(
            (
                (
                    row["key"],
                    Value(
                        _codata_float(row["value"]),
                        row["unit"],
                        dataset.source,
                        0.0
                        if row["uncertainty"] == "(exact)"
                        else _codata_float(row["uncertainty"]),
                        "",
                        name=row["quantity"],
                    ),
                )
                for row in dataset.rows
            ),
            name_of=lambda value: value.name,
        )
    return releases


def _load_constants(codata: Mapping[str, Value]) -> ConstantCollection:
    dataset = load_dataset(DATA_DIR / "constants" / "constants.csv")
    defined: dict[str, Value] = {}
    names = ChainMap(defined, dict(codata))
    for row in dataset.rows:
        expression = row["expression"]
        result = evaluate(expression, names)
        source = row["source"] or "; ".join(
            dict.fromkeys(value.source for value in result.inputs)
        )
        if not source:
            raise ValueError(f"{row['key']}: a literal value needs a source column.")
        notes = [row["notes"]] if row["notes"] else []
        if result.inputs:
            notes.append(f"Computed as {expression}.")
        defined[row["key"]] = Value(
            result.value,
            row["unit"],
            source,
            result.uncertainty,
            " ".join(notes),
            name=row["key"],
        )
    return ConstantCollection(defined.items(), name_of=lambda value: value.name)


codata: Mapping[int, ConstantCollection] = MappingProxyType(_load_codata())
phys = codata[max(codata)]
constants = _load_constants(phys)
constants.phys = phys
for _year, _release in codata.items():
    setattr(constants, f"codata{_year}", _release)


def __getattr__(key: str) -> Any:
    """Expose curated constants and `codataYYYY` releases as module attributes."""
    if key in constants:
        return constants[key]
    if key.startswith("codata") and key[6:].isdigit() and int(key[6:]) in codata:
        return codata[int(key[6:])]
    raise AttributeError(f"module {__name__!r} has no attribute {key!r}")


def __dir__() -> list[str]:
    return sorted([*globals(), *constants, *(f"codata{year}" for year in codata)])


__all__ = ["ConstantCollection", "codata", "constants", "phys", *constants]
