from dataclasses import dataclass

import pytest

from qcref.collections import Collection


@dataclass(frozen=True)
class Item:
    name: str


def make(*pairs: tuple[str, str]) -> Collection[Item]:
    return Collection(
        ((key, Item(name)) for key, name in pairs), name_of=lambda i: i.name
    )


def test_attribute_and_item_access_use_the_same_key():
    collection = make(("A_B", "A-B"))
    # getattr: a bare Collection has no generated key declarations for mypy
    assert getattr(collection, "A_B") is collection["A_B"] is collection.by_name("a-b")
    assert list(collection) == collection.as_list() == ["A_B"]
    assert "A_B" in dir(collection)
    with pytest.raises(KeyError):
        collection["A-B"]
    with pytest.raises(AttributeError):
        getattr(collection, "a_b")


@pytest.mark.parametrize("key", ["lower", "_LEADING", "1ABC", "A-B"])
def test_invalid_keys_rejected(key):
    with pytest.raises(ValueError):
        make((key, "x"))


def test_duplicate_keys_rejected():
    with pytest.raises(ValueError):
        make(("A", "x"), ("A", "y"))


def test_duplicate_names_rejected():
    with pytest.raises(ValueError):
        make(("A", "Name"), ("B", "name"))
