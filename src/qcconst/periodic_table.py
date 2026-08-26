"""Periodic table data sourced from PubChem and literature radii tables."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .collections import NamedCollection, normalize_name
from .constants import constants
from .models import Value
from .utils import to_table


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
    cov_radius_double: Optional[Value]
    cov_radius_triple: Optional[Value]
    vdw_radius: Optional[Value]


class PeriodicTable(NamedCollection[Element]):
    @classmethod
    def from_data(cls) -> "PeriodicTable":
        element_data: dict[str, dict[str, object]] = {}
        data_dir = Path(__file__).parent / "data"

        with (data_dir / "group_period.csv").open() as file:
            reader = csv.DictReader(file)
            for row in reader:
                element_data[row["Symbol"]] = {
                    "group": int(row["Group"]) if row["Group"] else None,
                    "period": int(row["Period"]),
                }

        with (data_dir / "covalent_radii_cordero_2008.csv").open() as file:
            reader = csv.DictReader(file)
            for row in reader:
                symbol = row["symbol"]
                notes = ""

                if symbol == "Csp3":
                    symbol = "C"
                    sp2_row = next(reader)
                    sp_row = next(reader)
                    notes = (
                        "Using sp3 hybridized carbon. "
                        f"sp2 and sp values are {float(sp2_row['cov_radius']) * constants.angstrom_to_bohr} "
                        f"and {float(sp_row['cov_radius']) * constants.angstrom_to_bohr} Bohr respectively."
                    )

                if "l.s." in symbol:
                    symbol = symbol.replace(" l.s.", "")
                    hs_row = next(reader)
                    notes = (
                        f"Using low spin value for {symbol}. "
                        f"High spin value is {float(hs_row['cov_radius']) * constants.angstrom_to_bohr} Bohr."
                    )

                element_data[symbol]["cov_radius"] = Value(
                    float(row["cov_radius"]) * constants.angstrom_to_bohr,
                    unit="Bohr",
                    source="Cordero et al. 2008: https://doi.org/10.1039/b801115j",
                    uncertainty=float(row["est_std_dev"])
                    * 0.01
                    * constants.angstrom_to_bohr
                    if row["est_std_dev"]
                    else None,
                    notes=notes,
                )

        with (data_dir / "covalent_radii_pyykko_2009.csv").open() as file:
            reader = csv.DictReader(file)
            for row in reader:
                symbol = row["symbol"]
                element_data[symbol]["cov_radius_double"] = (
                    Value(
                        float(row["r2"]) / 100 * constants.angstrom_to_bohr,
                        unit="Bohr",
                        source="Pyykkö et al. 2009: https://doi.org/10.1002/chem.200901472",
                        uncertainty=None,
                        notes="",
                    )
                    if row["r2"]
                    else None
                )
                element_data[symbol]["cov_radius_triple"] = (
                    Value(
                        float(row["r3"]) / 100 * constants.angstrom_to_bohr,
                        unit="Bohr",
                        source="Pyykkö et al. 2009: https://doi.org/10.1002/chem.200901472",
                        uncertainty=None,
                        notes="",
                    )
                    if row["r3"]
                    else None
                )

        with (data_dir / "vdw_radii_alvarez_2013.csv").open() as file:
            reader = csv.DictReader(file)
            for row in reader:
                symbol = row["symbol"]
                element_data[symbol]["vdw_radius"] = Value(
                    float(row["vdw_radius"].translate(str.maketrans("", "", "[]")))
                    * constants.angstrom_to_bohr,
                    unit="Bohr",
                    source="Alvarez 2013: https://doi.org/10.1039/C3DT50599E",
                    uncertainty=None,
                    notes=row["notes"],
                )

        elements: list[Element] = []
        with (data_dir / "pubchem.csv").open() as file:
            reader = csv.DictReader(file)
            pubchem_source = "PubChem: https://pubchem.ncbi.nlm.nih.gov/periodic-table"
            for row in reader:
                symbol = row["Symbol"]
                elements.append(
                    Element(
                        symbol=symbol,
                        number=int(row["AtomicNumber"]),
                        name=row["Name"],
                        mass=Value(row["AtomicMass"], "amu", pubchem_source, None, ""),
                        group=element_data[symbol]["group"],  # type: ignore[index]
                        period=element_data[symbol]["period"],  # type: ignore[index]
                        block=row["GroupBlock"],
                        electron_config=row["ElectronConfiguration"],
                        electronegativity=Value(
                            row["Electronegativity"], "Pauling", pubchem_source, None, ""
                        )
                        if row["Electronegativity"]
                        else None,
                        atomic_radius=Value(
                            float(row["AtomicRadius"]) / 100 * constants.angstrom_to_bohr,
                            "Bohr",
                            pubchem_source,
                            None,
                            "",
                        )
                        if row["AtomicRadius"]
                        else None,
                        cov_radius=element_data[symbol].get("cov_radius"),  # type: ignore[arg-type]
                        cov_radius_double=element_data[symbol].get("cov_radius_double"),  # type: ignore[arg-type]
                        cov_radius_triple=element_data[symbol].get("cov_radius_triple"),  # type: ignore[arg-type]
                        vdw_radius=element_data[symbol].get("vdw_radius"),  # type: ignore[arg-type]
                    )
                )

        return cls(
            elements,
            source_name=lambda element: element.symbol,
            canonical_key=lambda element: normalize_name(element.symbol),
            aliases=lambda element: [element.name],
        )

    def group(self, group_number: int) -> list[Element]:
        assert 1 <= group_number <= 18, "Group number must be between 1 and 18."
        return [element for element in self.values() if element.group == group_number]

    def period(self, period_number: int) -> list[Element]:
        assert 1 <= period_number <= 7, "Period number must be between 1 and 7."
        return [element for element in self.values() if element.period == period_number]

    def number(self, number: int) -> Element:
        for element in self.values():
            if element.number == number:
                return element
        raise ValueError(f"No atom with atomic number {number}.")

    @property
    def sources(self) -> list[str]:
        sources = set()
        for element in self.values():
            sources.add(element.mass.source)
            if element.electronegativity:
                sources.add(element.electronegativity.source)
            if element.atomic_radius:
                sources.add(element.atomic_radius.source)
            if element.cov_radius:
                sources.add(element.cov_radius.source)
            if element.cov_radius_double:
                sources.add(element.cov_radius_double.source)
            if element.cov_radius_triple:
                sources.add(element.cov_radius_triple.source)
            if element.vdw_radius:
                sources.add(element.vdw_radius.source)
        return sorted(sources)

    def show(self) -> None:
        rows = [
            {
                "key": key,
                "symbol": element.symbol,
                "name": element.name,
                "number": element.number,
                "group": element.group,
                "period": element.period,
                "mass": float(element.mass),
            }
            for key, element in self.items()
        ]
        to_table(rows)


periodic_table = PeriodicTable.from_data()

__all__ = ["Element", "PeriodicTable", "periodic_table"]
