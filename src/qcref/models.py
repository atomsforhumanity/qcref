"""Numeric reference values that carry their unit, source, and uncertainty."""

from __future__ import annotations

from typing import SupportsFloat, SupportsIndex


class Value(float):
    """A float subclass holding additional metadata.

    Every Value must have a non-empty source. Uncertainty should be set to 0.0 for
    exact values, None if not applicable or no data is available.
    """

    unit: str
    source: str
    uncertainty: float | None
    notes: str
    name: str

    def __new__(
        cls,
        value: str | SupportsFloat | SupportsIndex,
        unit: str,
        source: str,
        uncertainty: float | None,
        notes: str,
        name: str = "",
    ) -> Value:
        """Create a Value.

        Args:
            value: The number, or anything `float()` accepts.
            unit: Unit of the value; empty for dimensionless quantities.
            source: Citation for the value; must not be blank.
            uncertainty: Standard uncertainty in the same unit; 0.0 for exact
                values, None if unknown or not applicable.
            notes: Free-text remarks about the value.
            name: Original (source) name of the quantity, if any.

        Raises:
            ValueError: If ``source`` is empty or blank.
        """
        if not source or not source.strip():
            raise ValueError("Every Value must have a source.")
        obj = float.__new__(cls, value)
        obj.unit = unit
        obj.source = source
        obj.uncertainty = uncertainty
        obj.notes = notes
        obj.name = name
        return obj

    def __repr__(self) -> str:
        """Return the number followed by its metadata."""
        pieces = [
            str(float(self)),
            f"unit={self.unit}",
            f"uncertainty={self.uncertainty}",
            f"source={self.source}",
        ]
        if self.name:
            pieces.append(f"name={self.name}")
        if self.notes:
            pieces.append(f"notes={self.notes}")
        return ", ".join(pieces)
