import pytest

from qcconst import constants, phys
from qcconst.constants import BOHR_TO_ANGSTROM, codata


def test_constants_collection_access():
    bohr = constants.BOHR_TO_ANGSTROM
    assert bohr is constants["BOHR_TO_ANGSTROM"] is BOHR_TO_ANGSTROM
    assert bohr.name == "BOHR_TO_ANGSTROM"
    assert bohr.unit
    assert bohr.source


def test_constants_collection_metadata():
    assert "BOHR_TO_ANGSTROM" in constants.as_list()
    assert "BOHR_TO_ANGSTROM" in dir(constants)
    assert isinstance(constants.sources, list)


def test_codata_access():
    c = phys.SPEED_OF_LIGHT_IN_VACUUM
    assert (
        c
        is phys["SPEED_OF_LIGHT_IN_VACUUM"]
        is phys.by_name("speed of light in vacuum")
    )
    assert c == 299792458.0
    assert c.name == "speed of light in vacuum"
    assert constants.phys is phys is constants.codata2022


def test_codata_releases():
    assert codata[max(codata)] is phys
    assert constants.codata2022 is codata[2022]


def test_curated_constants_follow_codata():
    bohr = constants.BOHR_TO_ANGSTROM
    assert bohr == pytest.approx(phys.BOHR_RADIUS * 1e10, rel=1e-15)
    assert bohr.uncertainty == pytest.approx(phys.BOHR_RADIUS.uncertainty * 1e10)
    assert bohr.source == phys.BOHR_RADIUS.source
    assert "BOHR_RADIUS * 1e10" in bohr.notes
    inverse = constants.ANGSTROM_TO_BOHR
    assert inverse.uncertainty / inverse == pytest.approx(bohr.uncertainty / bohr)


def test_literal_constant_uses_row_source():
    kcal = constants.KCAL_TO_JOULE
    assert kcal == 4184.0
    assert kcal.uncertainty == 0.0
    assert "NIST SP 811" in kcal.source
    assert "NIST SP 811" in constants.HARTREE_TO_KCAL_PER_MOL.source


def test_constants_show():
    constants.show()
