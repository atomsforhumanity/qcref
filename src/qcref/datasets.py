"""Load CSV datasets and their required `.meta.json` source metadata.

Every `data/<dataset>/<name>.csv` file has a `<name>.meta.json` sidecar:

    {
      "source": "Short citation: https://doi.org/...",   # required
      "citation": "Full bibliographic reference",        # optional
      "notes": "Anything a user should know",            # optional
      "columns": {"cov_radius": {"unit": "Å"}}           # optional
    }

`source` becomes the `.source` of every value loaded from the file.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent / "data"


@dataclass(frozen=True)
class Dataset:
    path: Path
    meta: dict[str, Any]
    rows: list[dict[str, str]]

    @property
    def source(self) -> str:
        return self.meta["source"]

    def unit(self, column: str) -> str:
        """The unit of a column as published in the source."""
        try:
            return self.meta["columns"][column]["unit"]
        except KeyError:
            raise KeyError(
                f"{self.path.name}: no unit declared for {column!r}"
            ) from None


def load_dataset(path: Path) -> Dataset:
    meta_path = path.with_suffix(".meta.json")
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise FileNotFoundError(f"{path.name} has no metadata file {meta_path.name}")
    if not isinstance(meta.get("source"), str) or not meta["source"].strip():
        raise ValueError(f"{meta_path.name} must declare a non-empty 'source'.")
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return Dataset(path, meta, rows)


def dataset_paths(dataset: str) -> list[Path]:
    """All CSV files of a dataset, sorted by name."""
    return sorted((DATA_DIR / dataset).glob("*.csv"))
