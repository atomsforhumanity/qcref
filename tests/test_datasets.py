import dataclasses
import json

import pytest

from qcref import constants, periodic_table, solvents
from qcref.constants import codata
from qcref.datasets import DATA_DIR, load_dataset
from qcref.models import Value

CSV_PATHS = sorted(DATA_DIR.glob("*/*.csv"))


@pytest.mark.parametrize("path", CSV_PATHS, ids=lambda p: f"{p.parent.name}/{p.name}")
def test_every_dataset_has_source_metadata(path):
    dataset = load_dataset(path)
    assert dataset.rows
    for column in dataset.meta.get("columns", {}):
        assert column in dataset.rows[0], f"{column} declared but not in CSV"


def test_no_orphan_metadata():
    for meta in DATA_DIR.glob("*/*.meta.json"):
        assert meta.with_name(meta.name.replace(".meta.json", ".csv")).exists()
        json.loads(meta.read_text(encoding="utf-8"))


def test_value_requires_source():
    with pytest.raises(ValueError):
        Value(1.0, "m", "", None, "")


def _values():
    for collection in [constants, *codata.values()]:
        yield from collection.values()
    for element in periodic_table.values():
        for field in dataclasses.fields(element):
            yield getattr(element, field.name)
    for solvent in solvents.values():
        yield solvent.dielectric


def test_every_loaded_value_has_source():
    for value in _values():
        if isinstance(value, Value):
            assert value.source.strip()
