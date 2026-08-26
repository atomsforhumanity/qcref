import pytest

from qcconst import PeriodicTable
from qcconst import periodic_table as pt


def test_periodic_table_from_pubchem():
    PeriodicTable.from_data()


def test_periodic_table_collection_access():
    assert pt.ni == pt["ni"] == pt["Ni"] == pt["Nickel"]
    assert pt.ni.symbol == "Ni"
    assert "ni" in pt.as_list()
    assert "Ni" not in dir(pt)


def test_group_period_lookup_params():
    with pytest.raises(AssertionError):
        pt.group(0)
    with pytest.raises(AssertionError):
        pt.group(19)
    with pytest.raises(AssertionError):
        pt.period(0)
    with pytest.raises(AssertionError):
        pt.period(8)


def test_group_and_period_data():
    assert [a.symbol for a in pt.group(1)] == ["H", "Li", "Na", "K", "Rb", "Cs", "Fr"]
    assert [a.symbol for a in pt.group(10)] == ["Ni", "Pd", "Pt", "Ds"]
    assert [a.symbol for a in pt.period(4)] == [
        "K",
        "Ca",
        "Sc",
        "Ti",
        "V",
        "Cr",
        "Mn",
        "Fe",
        "Co",
        "Ni",
        "Cu",
        "Zn",
        "Ga",
        "Ge",
        "As",
        "Se",
        "Br",
        "Kr",
    ]


def test_number_and_sources():
    assert pt.number(1).symbol == "H"
    assert pt.number(118).symbol == "Og"
    with pytest.raises(ValueError):
        pt.number(0)
    assert isinstance(pt.sources, list)


def test_show():
    pt.show()
