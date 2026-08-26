from qcconst import constants, phys


def test_constants_collection_access():
    bohr = constants.bohr_to_angstrom
    assert bohr == constants["bohr_to_angstrom"]
    assert bohr == constants["BOHR_TO_ANGSTROM"]
    assert bohr.name == "BOHR_TO_ANGSTROM"
    assert bohr.unit
    assert bohr.source


def test_constants_collection_metadata():
    assert "bohr_to_angstrom" in constants.as_list()
    assert "BOHR_TO_ANGSTROM" not in dir(constants)
    assert isinstance(constants.sources, list)
    assert phys["atomic unit of permittivity"].name == "atomic unit of permittivity"


def test_constants_show():
    constants.show()
