"""CRC-based solvent permittivity data."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .collections import NamedCollection
from .utils import to_table

CRC_SOURCE = "CRC Handbook of Chemistry and Physics, Permittivity (Dielectric Constant) of Liquids"


@dataclass(frozen=True)
class DielectricFit:
    a: float
    b: float = 0.0
    c: float = 0.0
    d: float = 0.0
    t_min_k: float | None = None
    t_max_k: float | None = None

    def evaluate(self, T: float, strict: bool = True) -> float:
        if strict:
            if self.t_min_k is not None and T < self.t_min_k:
                raise ValueError(f"Temperature {T} K is below the fit range.")
            if self.t_max_k is not None and T > self.t_max_k:
                raise ValueError(f"Temperature {T} K is above the fit range.")
        return self.a + self.b * T + self.c * T**2 + self.d * T**3


@dataclass(frozen=True)
class Solvent:
    name: str
    formula: str | None
    dielectric: float
    dielectric_temperature_k: float | None
    fit: DielectricFit | None
    sources: list[str]

    @property
    def has_temperature_fit(self) -> bool:
        return self.fit is not None

    def dielectric_at(self, T: float, strict: bool = True) -> float:
        if self.fit is None:
            raise ValueError(f"{self.name} does not have a temperature-dependent dielectric fit.")
        return self.fit.evaluate(T, strict=strict)


class SolventCollection(NamedCollection[Solvent]):
    def show(self) -> None:
        rows = [
            {
                "key": key,
                "name": solvent.name,
                "formula": solvent.formula,
                "dielectric": solvent.dielectric,
                "temp_k": solvent.dielectric_temperature_k,
                "fit": "yes" if solvent.fit else "",
                "source": "; ".join(solvent.sources),
            }
            for key, solvent in self.items()
        ]
        to_table(rows)


def _optional_float(value: str) -> float | None:
    return float(value) if value else None


def _load_solvents(csv_path: Path) -> SolventCollection:
    solvent_entries: list[Solvent] = []
    key_by_id: dict[int, str] = {}
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            fit_values = [
                _optional_float(row["fit_a"]),
                _optional_float(row["fit_b"]),
                _optional_float(row["fit_c"]),
                _optional_float(row["fit_d"]),
            ]
            fit = (
                DielectricFit(
                    a=fit_values[0] if fit_values[0] is not None else 0.0,
                    b=fit_values[1] or 0.0,
                    c=fit_values[2] or 0.0,
                    d=fit_values[3] or 0.0,
                    t_min_k=_optional_float(row["t_min_k"]),
                    t_max_k=_optional_float(row["t_max_k"]),
                )
                if fit_values[0] is not None
                else None
            )
            solvent = Solvent(
                name=row["name"],
                formula=row["formula"] or None,
                dielectric=float(row["dielectric"]),
                dielectric_temperature_k=_optional_float(row["dielectric_temperature_k"]),
                fit=fit,
                sources=[s for s in row["sources"].split(";") if s],
            )
            solvent_entries.append(solvent)
            key_by_id[id(solvent)] = row["normalized_key"]
    return SolventCollection(
        solvent_entries,
        source_name=lambda solvent: solvent.name,
        canonical_key=lambda solvent: key_by_id[id(solvent)],
    )


solvents = _load_solvents(Path(__file__).parent / "data" / "solvents.csv")

__all__ = ["CRC_SOURCE", "DielectricFit", "Solvent", "SolventCollection", "solvents"]
