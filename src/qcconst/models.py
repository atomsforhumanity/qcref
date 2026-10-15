from typing import Optional


class Value(float):
    """A float subclass holding additional metadata.

    Uncertainty should be set to 0.0 for exact values, None if not applicable or no
    data is available.
    """

    unit: str
    source: str
    uncertainty: Optional[float]
    notes: str
    name: str

    def __new__(
        cls,
        value,
        unit: str,
        source: str,
        uncertainty: Optional[float],
        notes: str,
        name: str = "",
    ):
        obj = float.__new__(cls, value)
        obj.unit = unit
        obj.source = source
        obj.uncertainty = uncertainty
        obj.notes = notes
        obj.name = name
        return obj

    def __repr__(self):
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
