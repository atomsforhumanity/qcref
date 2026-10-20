import csv
from pathlib import Path

import pytest

from qcref import dftb_parameter_sets
from qcref.dftb import ANGULAR_MOMENTA


def test_parameter_set_access():
    ob3 = dftb_parameter_sets.OB3_3_1
    assert (
        ob3 is dftb_parameter_sets["OB3_3_1"] is dftb_parameter_sets.by_name("3ob-3-1")
    )
    assert dftb_parameter_sets.by_name("MIO-1-1") is dftb_parameter_sets.MIO_1_1
    assert ob3.model == "DFTB3" and ob3.third_order
    assert not dftb_parameter_sets.MIO_1_1.third_order
    assert ob3.license == dftb_parameter_sets.MIO_1_1.license == "CC-BY-SA-4.0"


def test_3ob_values_as_published():
    """Values from the 3ob-3-1 README, with the README as their source."""
    ob3 = dftb_parameter_sets.OB3_3_1
    assert ob3.h_damping_exponent == 4.0
    oxygen = ob3.elements["O"]
    assert oxygen.max_angular_momentum == "p"
    assert oxygen.hubbard_derivative == -0.1575
    assert oxygen.hubbard_derivative.unit == "a.u."
    assert "3ob" in oxygen.hubbard_derivative.source
    assert ob3.elements["H"].max_angular_momentum == "s"
    assert ob3.elements["Zn"].hubbard_derivative == -0.03
    assert len(ob3.elements) == 15
    assert "J. Chem. Theory Comput., 2013, 9, 338-354" in ob3.citation


def test_mio_has_no_dftb3_settings():
    """mio-1-1 is an SCC-DFTB set: angular momenta only, no damping."""
    mio = dftb_parameter_sets.MIO_1_1
    assert mio.h_damping_exponent is None
    assert {e: v.max_angular_momentum for e, v in mio.elements.items()} == {
        "C": "p",
        "H": "s",
        "N": "p",
        "O": "p",
        "P": "d",
        "S": "d",
    }
    assert all(v.hubbard_derivative is None for v in mio.elements.values())
    assert "wfc.hsd" in mio.source


@pytest.mark.parametrize("name", ["3ob-3-1", "mio-1-1"])
def test_element_csv_schema(name):
    with Path(f"src/qcref/data/dftb/{name}.csv").open() as f:
        rows = list(csv.DictReader(f))
    assert rows and all(row["max_angular_momentum"] in ANGULAR_MOMENTA for row in rows)
    symbols = [row["element"] for row in rows]
    assert len(symbols) == len(set(symbols))
