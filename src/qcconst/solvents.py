"""CRC-based solvent permittivity data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .collections import Collection
from .datasets import DATA_DIR, load_dataset
from .models import Value


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
    dielectric: Value
    dielectric_temperature_k: float | None
    fit: DielectricFit | None

    @property
    def source(self) -> str:
        """Source of the dielectric value and its temperature fit."""
        return self.dielectric.source

    @property
    def has_temperature_fit(self) -> bool:
        return self.fit is not None

    def dielectric_at(self, T: float, strict: bool = True) -> float:
        if self.fit is None:
            raise ValueError(
                f"{self.name} does not have a temperature-dependent dielectric fit."
            )
        return self.fit.evaluate(T, strict=strict)


class SolventCollection(Collection[Solvent]):
    def _row(self, entry: Solvent) -> dict[str, Any]:
        return {
            "name": entry.name,
            "formula": entry.formula,
            "dielectric": float(entry.dielectric),
            "temp_k": entry.dielectric_temperature_k,
            "fit": "yes" if entry.fit else "",
            "source": entry.source,
        }


def _optional_float(value: str) -> float | None:
    return float(value) if value else None


def _load_solvents() -> SolventCollection:
    dataset = load_dataset(DATA_DIR / "solvents" / "crc.csv")
    entries: list[tuple[str, Solvent]] = []
    for row in dataset.rows:
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
            dielectric=Value(
                row["dielectric"], dataset.unit("dielectric"), dataset.source, None, ""
            ),
            dielectric_temperature_k=_optional_float(row["dielectric_temperature_k"]),
            fit=fit,
        )
        entries.append((row["key"], solvent))
    return SolventCollection(entries, name_of=lambda solvent: solvent.name)


solvents = _load_solvents()

__all__ = ["DielectricFit", "Solvent", "SolventCollection", "solvents"]
