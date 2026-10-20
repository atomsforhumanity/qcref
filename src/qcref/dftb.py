"""Settings that DFTB Slater-Koster parameter sets prescribe for their use.

A DFTB calculation needs more than the Slater-Koster files: each set's documentation
lists the maximum angular momentum of every element and, for DFTB3 sets, the atomic
Hubbard derivatives and the H-bond damping exponent. These are properties of the
parameter set, the same in every DFTB program. The Slater-Koster files themselves are
not included; download them from each set's ``url``.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ._keys import DFTBParameterSetKeys
from .collections import Collection
from .datasets import DATA_DIR, load_dataset
from .models import Value

ANGULAR_MOMENTA = ("s", "p", "d", "f")


@dataclass(frozen=True)
class DFTBElement:
    """An element's settings in a DFTB parameter set.

    Attributes:
        symbol: Element symbol.
        max_angular_momentum: Highest angular momentum of the element's basis, one of
            ``"s"``, ``"p"``, ``"d"``, ``"f"``.
        hubbard_derivative: Atomic Hubbard derivative for DFTB3 in atomic units, or
            None if the set does not define one.
    """

    symbol: str
    max_angular_momentum: str
    hubbard_derivative: Value | None


@dataclass(frozen=True)
class DFTBParameterSet:
    """A Slater-Koster parameter set and the settings its documentation prescribes.

    Attributes:
        name: The set's name, e.g. ``"3ob-3-1"``.
        version: Release of the set the data come from.
        model: DFTB Hamiltonian the set was parametrized for, ``"DFTB3"`` or
            ``"SCC-DFTB"``.
        h_damping_exponent: Exponent zeta of the gamma^h H-bond damping, or None if
            the set prescribes none.
        url: Where to download the set's Slater-Koster files.
        license: SPDX license identifier of the set.
        elements: Per-element settings, keyed by element symbol.
        source: Where the per-element settings were published.
        citation: The set's copyright and the references its license requires.
    """

    name: str
    version: str
    model: str
    h_damping_exponent: Value | None
    url: str
    license: str
    elements: Mapping[str, DFTBElement]
    source: str
    citation: str

    @property
    def third_order(self) -> bool:
        """Whether the set is meant for third-order DFTB (DFTB3)."""
        return self.model == "DFTB3"


class DFTBParameterSetCollection(DFTBParameterSetKeys, Collection[DFTBParameterSet]):
    """Collection of DFTB parameter sets, such as ``dftb_parameter_sets.MIO_1_1``.

    Look a set up by its own name with ``by_name("3ob-3-1")``.
    """

    def _row(self, entry: DFTBParameterSet) -> dict[str, Any]:
        return {
            "name": entry.name,
            "version": entry.version,
            "model": entry.model,
            "elements": " ".join(entry.elements),
            "license": entry.license,
        }


def _load_elements(name: str) -> tuple[dict[str, DFTBElement], str, str]:
    dataset = load_dataset(DATA_DIR / "dftb" / f"{name}.csv")
    elements: dict[str, DFTBElement] = {}
    for row in dataset.rows:
        momentum = row["max_angular_momentum"]
        if momentum not in ANGULAR_MOMENTA:
            raise ValueError(
                f"{name}: {row['element']} has unknown angular momentum {momentum!r}."
            )
        derivative = row["hubbard_derivative"]
        elements[row["element"]] = DFTBElement(
            symbol=row["element"],
            max_angular_momentum=momentum,
            hubbard_derivative=(
                Value(
                    derivative,
                    dataset.unit("hubbard_derivative"),
                    dataset.source,
                    None,
                    "",
                )
                if derivative
                else None
            ),
        )
    return elements, dataset.source, dataset.meta.get("citation", "")


def _load_parameter_sets() -> DFTBParameterSetCollection:
    dataset = load_dataset(DATA_DIR / "dftb" / "parameter_sets.csv")
    entries: list[tuple[str, DFTBParameterSet]] = []
    for row in dataset.rows:
        elements, source, citation = _load_elements(row["name"])
        exponent = row["h_damping_exponent"]
        entries.append(
            (
                row["key"],
                DFTBParameterSet(
                    name=row["name"],
                    version=row["version"],
                    model=row["model"],
                    h_damping_exponent=(
                        Value(
                            exponent,
                            dataset.unit("h_damping_exponent"),
                            dataset.source,
                            None,
                            "",
                        )
                        if exponent
                        else None
                    ),
                    url=row["url"],
                    license=row["license"],
                    elements=elements,
                    source=source,
                    citation=citation,
                ),
            )
        )
    return DFTBParameterSetCollection(entries, name_of=lambda entry: entry.name)


dftb_parameter_sets = _load_parameter_sets()

__all__ = [
    "DFTBElement",
    "DFTBParameterSet",
    "DFTBParameterSetCollection",
    "dftb_parameter_sets",
]
