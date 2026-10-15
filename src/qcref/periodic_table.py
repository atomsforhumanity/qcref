"""Periodic table data sourced from PubChem, IUPAC, and literature radii tables.

Radii are stored in the CSVs as published (Å or pm) and converted to Bohr here,
using the unit declared for each column in the dataset's metadata.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, ClassVar

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
    """A chemical element and its properties.

    Radii are in Bohr; properties missing from the sources are None.

    Attributes:
        symbol: Element symbol, such as ``"Fe"``.
        number: Atomic number.
        name: Element name.
        mass: Atomic mass in amu (PubChem).
        group: Group number (1-18), or None if the element has no group.
        period: Period number (1-7).
        block: PubChem group block, such as ``"Noble gas"``.
        electron_config: Ground-state electron configuration (PubChem).
        electronegativity: Pauling electronegativity (PubChem).
        atomic_radius: Atomic radius (PubChem).
        cov_radius: Covalent radius (Cordero et al., 2008).
        cov_radius_single: Single-bond covalent radius (Pyykko, 2015).
        cov_radius_double: Double-bond covalent radius (Pyykko, 2015).
        cov_radius_triple: Triple-bond covalent radius (Pyykko, 2015).
        vdw_radius: Van der Waals radius (Alvarez, 2013).
    """

    symbol: str
    number: int
    name: str
    mass: Value
    group: int | None
    period: int
    block: str
    electron_config: str
    electronegativity: Value | None
    atomic_radius: Value | None
    cov_radius: Value | None
    cov_radius_single: Value | None
    cov_radius_double: Value | None
    cov_radius_triple: Value | None
    vdw_radius: Value | None


def _value(dataset: Dataset, column: str, raw: str, notes: str = "") -> Value | None:
    """A Value in the column's published unit, or None if the cell is empty."""
    if not raw:
        return None
    return Value(raw, dataset.unit(column), dataset.source, None, notes)


def _bohr(
    dataset: Dataset,
    column: str,
    raw: str,
    notes: str = "",
    uncertainty: float | None = None,
) -> Value | None:
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
    """Collection of elements keyed by symbol, such as ``periodic_table.Fe``."""

    key_pattern: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Z][a-z]{0,2}$")
    _datasets: list[Dataset]

    @classmethod
    def from_data(cls) -> PeriodicTable:
        """Build the table from the bundled element datasets."""
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

        def cov_radius(symbol: str) -> Value | None:
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

        def vdw_radius(symbol: str) -> Value | None:
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
        """Return the elements in a group.

        Args:
            group_number: Group number, from 1 to 18.

        Raises:
            ValueError: If ``group_number`` is outside 1-18.
        """
        if not 1 <= group_number <= 18:
            raise ValueError("Group number must be between 1 and 18.")
        return [element for element in self.values() if element.group == group_number]

    def period(self, period_number: int) -> list[Element]:
        """Return the elements in a period.

        Args:
            period_number: Period number, from 1 to 7.

        Raises:
            ValueError: If ``period_number`` is outside 1-7.
        """
        if not 1 <= period_number <= 7:
            raise ValueError("Period number must be between 1 and 7.")
        return [element for element in self.values() if element.period == period_number]

    def number(self, number: int) -> Element:
        """Return the element with the given atomic number.

        Raises:
            ValueError: If no element has that atomic number.
        """
        for element in self.values():
            if element.number == number:
                return element
        raise ValueError(f"No atom with atomic number {number}.")

    @property
    def sources(self) -> list[str]:
        """Sources of the underlying datasets, sorted."""
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
