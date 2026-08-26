import csv
from pathlib import Path

import pytest

from qcconst import solvents
from qcconst.solvents import DielectricFit


def test_solvent_collection_access():
    acetone = solvents.acetone
    assert acetone == solvents["acetone"] == solvents["Acetone"]
    assert solvents._1_4_dioxane == solvents["1,4-Dioxane"]
    assert acetone.dielectric > 0
    assert acetone.dielectric_temperature_k == 293.15
    assert acetone.sources


def test_dielectric_fit_evaluation():
    fit = DielectricFit(a=1.0, b=2.0, c=3.0, d=4.0, t_min_k=200.0, t_max_k=400.0)
    assert fit.evaluate(2.0, strict=False) == 49.0
    with pytest.raises(ValueError):
        fit.evaluate(150.0)


def test_solvent_temperature_fit_loading():
    assert solvents.acetone.fit is not None
    assert solvents.acetone.dielectric_at(298.15, strict=False) == pytest.approx(
        20.49331470812499
    )
    assert solvents.acetaldehyde.fit is None
    with pytest.raises(ValueError):
        solvents.acetaldehyde.dielectric_at(298.15)


def test_solvent_csv_schema():
    with Path("src/qcconst/data/solvents.csv").open() as f:
        rows = list(csv.DictReader(f))
    assert rows
    assert {
        "name",
        "normalized_key",
        "formula",
        "dielectric",
        "dielectric_temperature_k",
        "fit_a",
        "fit_b",
        "fit_c",
        "fit_d",
        "t_min_k",
        "t_max_k",
        "sources",
    } == set(rows[0])
    water = next(row for row in rows if row["name"] == "Water")
    assert water["dielectric_temperature_k"] == "293.15"


def test_show():
    solvents.show()
