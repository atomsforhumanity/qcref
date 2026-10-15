import pytest

from qcref import PeriodicTable
from qcref import periodic_table as pt


def test_periodic_table_from_pubchem():
    PeriodicTable.from_data()


def test_periodic_table_collection_access():
    assert pt.Ni is pt["Ni"] is pt.by_name("Nickel") is pt.by_name("nickel")
    assert pt.Ni.symbol == "Ni"
    assert pt["As"].name == "Arsenic"
    assert "Ni" in pt.as_list()
    assert "Ni" in dir(pt)


def test_periodic_table_rejects_non_keys():
    with pytest.raises(AttributeError):
        _ = pt.ni
    with pytest.raises(KeyError):
        pt["Nickel"]
    with pytest.raises(KeyError):
        pt.by_name("Ni")


def test_group_period_lookup_params():
    with pytest.raises(ValueError):
        pt.group(0)
    with pytest.raises(ValueError):
        pt.group(19)
    with pytest.raises(ValueError):
        pt.period(0)
    with pytest.raises(ValueError):
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


def test_cordero_default_variants():
    carbon = pt.C.cov_radius
    assert carbon.source.startswith("Cordero")
    assert "Using Csp3" in carbon.notes and "Csp2 = 0.73 Å" in carbon.notes
    assert "Using Mn l.s." in pt.Mn.cov_radius.notes
    assert "Other values" not in pt.Ni.cov_radius.notes


def test_pyykko_bond_order_radii():
    carbon = pt.C
    assert (
        carbon.cov_radius_single > carbon.cov_radius_double > carbon.cov_radius_triple
    )
    assert carbon.cov_radius_single.unit == "Bohr"
    assert carbon.cov_radius_single.source.startswith("Pyykkö 2015")
    assert "Converted from 75 pm" in carbon.cov_radius_single.notes


def test_group_3_convention():
    assert [e.symbol for e in pt.group(3)] == ["Sc", "Y", "Lu", "Lr"]
    assert pt.La.group is None


def test_sources_cover_all_datasets():
    assert len(pt.sources) == 5
