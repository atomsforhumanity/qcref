from qcconst import constants, phys
from qcconst.constants import BOHR_TO_ANGSTROM


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


def test_constants_show():
    constants.show()
