"""Physical constants from NIST CODATA 2022 and related sources."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .collections import Collection
from .models import Value

_DATA_DIR = Path(__file__).parent / "data"


class ConstantCollection(Collection[Value]):
    codata2022: ConstantCollection
    phys: ConstantCollection

    @property
    def sources(self) -> list[str]:
        return sorted(
            {
                value.source
                for value in self.values()
                if not value.source.startswith("Derived")
            }
        )

    def _row(self, entry: Value) -> dict[str, Any]:
        return {
            "name": entry.name,
            "value": float(entry),
            "unit": entry.unit,
            "uncertainty": entry.uncertainty,
            "source": entry.source,
        }


def _load_constants(csv_path: Path) -> ConstantCollection:
    with csv_path.open(newline="") as f:
        entries = [
            (
                row["key"],
                Value(
                    row["value"],
                    row["unit"],
                    row["source"],
                    float(row["uncertainty"]) if row["uncertainty"] else None,
                    row["notes"],
                    name=row["key"],
                ),
            )
            for row in csv.DictReader(f)
        ]
    return ConstantCollection(entries, name_of=lambda value: value.name)


def _load_codata(year: int) -> ConstantCollection:
    source = f"CODATA {year}: https://physics.nist.gov/cuu/Constants/Table/allascii.txt"

    def _process_float(value: str) -> float:
        """Handle CODATA's spaces and ellipses in float values."""
        return float(value.replace(" ", "").replace("...", ""))

    with (_DATA_DIR / f"codata{year}.csv").open(newline="") as f:
        entries = [
            (
                row["key"],
                Value(
                    _process_float(row["value"]),
                    row["unit"],
                    source,
                    _process_float(row["uncertainty"])
                    if row["uncertainty"] != "(exact)"
                    else 0.0,
                    "",
                    name=row["quantity"],
                ),
            )
            for row in csv.DictReader(f)
        ]
    return ConstantCollection(entries, name_of=lambda value: value.name)


constants = _load_constants(_DATA_DIR / "constants.csv")
codata2022 = _load_codata(2022)
phys = codata2022
constants.codata2022 = codata2022
constants.phys = phys


def __getattr__(key: str) -> Value:
    """Expose curated constants as module attributes: `from qcconst.constants import X`."""
    try:
        return constants[key]
    except KeyError:
        raise AttributeError(f"module {__name__!r} has no attribute {key!r}") from None


def __dir__() -> list[str]:
    return sorted([*globals(), *constants])


__all__ = ["ConstantCollection", "constants", "codata2022", "phys", *constants]
