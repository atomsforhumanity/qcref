"""Periodic table data sourced from PubChem, IUPAC, and literature radii tables.

Radii are stored in the CSVs as published (Å or pm) and converted to Bohr here,
using the unit declared for each column in the dataset's metadata.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, ClassVar, Optional

from ._keys import PeriodicTableKeys
from .collections import Collection
from .constants import constants
from .datasets import DATA_DIR, Dataset, load_dataset
from .models import Value

_ELEMENTS_DIR = DATA_DIR / "elements"
_BOHR_PER_UNIT = {
    "Å": constants.ANGSTROM_TO_BOHR,
    "pm": constants.ANGSTROM_TO_BOHR / 100,
}


@dataclass(frozen=True)
class Element:
    symbol: str
    number: int
    name: str
    mass: Value
    group: Optional[int]
    period: int
    block: str
    electron_config: str
    electronegativity: Optional[Value]
    atomic_radius: Optional[Value]
    cov_radius: Optional[Value]
    cov_radius_single: Optional[Value]
    cov_radius_double: Optional[Value]
    cov_radius_triple: Optional[Value]
    vdw_radius: Optional[Value]


def _value(dataset: Dataset, column: str, raw: str, notes: str = "") -> Optional[Value]:
    """A Value in the column's published unit, or None if the cell is empty."""
    if not raw:
        return None
    return Value(raw, dataset.unit(column), dataset.source, None, notes)


def _bohr(
    dataset: Dataset,
    column: str,
    raw: str,
    notes: str = "",
    uncertainty: Optional[float] = None,
) -> Optional[Value]:
    """A length in Bohr converted from the column's published unit."""
    if not raw:
        return None
    unit = dataset.unit(column)
    converted = f"Converted from {raw} {unit}."
    return Value(
        float(raw) * _BOHR_PER_UNIT[unit],
        "Bohr",
        dataset.source,
        uncertainty,
        f"{notes} {converted}" if notes else converted,
    )


class PeriodicTable(PeriodicTableKeys, Collection[Element]):
    key_pattern: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Z][a-z]{0,2}$")
    _datasets: list[Dataset]

    @classmethod
    def from_data(cls) -> PeriodicTable:
        pubchem, group_period, cordero, pyykko, alvarez = datasets = [
            load_dataset(_ELEMENTS_DIR / f"{name}.csv")
            for name in (
                "pubchem",
                "group_period",
                "cordero_2008",
                "pyykko_2015",
                "alvarez_2013",
            )
        ]
        positions = {row["Symbol"]: row for row in group_period.rows}
        pyykko_rows = {row["symbol"]: row for row in pyykko.rows}
        alvarez_rows = {row["symbol"]: row for row in alvarez.rows}

        cordero_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in cordero.rows:
            cordero_rows[row["element"]].append(row)

        def cov_radius(symbol: str) -> Optional[Value]:
            rows = cordero_rows.get(symbol)
            if not rows:
                return None
            (default,) = [row for row in rows if row["default"] == "true"]
            others = ", ".join(
                f"{row['label']} = {row['cov_radius']} {cordero.unit('cov_radius')}"
                for row in rows
                if row is not default
            )
            std_dev = default["est_std_dev"]
            return _bohr(
                cordero,
                "cov_radius",
                default["cov_radius"],
                notes=f"Using {default['label']}. Other values in source: {others}."
                if others
                else "",
                uncertainty=float(std_dev) * _BOHR_PER_UNIT[cordero.unit("est_std_dev")]
                if std_dev
                else None,
            )

        def vdw_radius(symbol: str) -> Optional[Value]:
            row = alvarez_rows.get(symbol)
            if row is None:
                return None
            raw = row["vdw_radius"]
            notes = [row["notes"]] if row["notes"] else []
            if raw.startswith("["):
                notes.append("Value is bracketed in the source table.")
            return _bohr(alvarez, "vdw_radius", raw.strip("[]"), " ".join(notes))

        elements = []
        for row in pubchem.rows:
            symbol = row["Symbol"]
            position = positions[symbol]
            pyykko_row = pyykko_rows.get(symbol, {})
            elements.append(
                Element(
                    symbol=symbol,
                    number=int(row["AtomicNumber"]),
                    name=row["Name"],
                    mass=Value(
                        row["AtomicMass"],
                        pubchem.unit("AtomicMass"),
                        pubchem.source,
                        None,
                        "",
                    ),
                    group=int(position["Group"]) if position["Group"] else None,
                    period=int(position["Period"]),
                    block=row["GroupBlock"],
                    electron_config=row["ElectronConfiguration"],
                    electronegativity=_value(
                        pubchem, "Electronegativity", row["Electronegativity"]
                    ),
                    atomic_radius=_bohr(pubchem, "AtomicRadius", row["AtomicRadius"]),
                    cov_radius=cov_radius(symbol),
                    cov_radius_single=_bohr(pyykko, "r1", pyykko_row.get("r1", "")),
                    cov_radius_double=_bohr(pyykko, "r2", pyykko_row.get("r2", "")),
                    cov_radius_triple=_bohr(pyykko, "r3", pyykko_row.get("r3", "")),
                    vdw_radius=vdw_radius(symbol),
                )
            )

        table = cls(
            ((element.symbol, element) for element in elements),
            name_of=lambda element: element.name,
        )
        table._datasets = datasets
        return table

    def group(self, group_number: int) -> list[Element]:
        if not 1 <= group_number <= 18:
            raise ValueError("Group number must be between 1 and 18.")
        return [element for element in self.values() if element.group == group_number]

    def period(self, period_number: int) -> list[Element]:
        if not 1 <= period_number <= 7:
            raise ValueError("Period number must be between 1 and 7.")
        return [element for element in self.values() if element.period == period_number]

    def number(self, number: int) -> Element:
        for element in self.values():
            if element.number == number:
                return element
        raise ValueError(f"No atom with atomic number {number}.")

    @property
    def sources(self) -> list[str]:
        return sorted(dataset.source for dataset in self._datasets)

    def _row(self, entry: Element) -> dict[str, Any]:
        return {
            "name": entry.name,
            "number": entry.number,
            "group": entry.group,
            "period": entry.period,
            "mass": float(entry.mass),
        }


periodic_table = PeriodicTable.from_data()

__all__ = ["Element", "PeriodicTable", "periodic_table"]
