from dataclasses import dataclass

import pytest

from qcconst.collections import NamedCollection, normalize_name


@dataclass(frozen=True)
class Item:
    name: str


def test_normalize_name_examples():
    assert normalize_name("Acetone") == "acetone"
    assert normalize_name("1,4-dioxane") == "_1_4_dioxane"
    assert normalize_name("2,2,2-trifluoroethanol") == "_2_2_2_trifluoroethanol"
    assert normalize_name("N,N-dimethylformamide") == "n_n_dimethylformamide"
    assert normalize_name("BOHR_TO_ANGSTROM") == "bohr_to_angstrom"
    assert normalize_name("Ni") == "ni"


def test_collection_collision_handling():
    collection = NamedCollection(
        [Item("A-B"), Item("A B")],
        source_name=lambda item: item.name,
    )
    assert collection["A-B"].name == "A-B"
    assert collection["A B"].name == "A B"
    with pytest.raises(AttributeError):
        _ = collection.a_b
    with pytest.raises(KeyError):
        collection["a_b"]
