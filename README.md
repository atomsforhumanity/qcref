# qcref

[![image](https://img.shields.io/pypi/v/qcref.svg)](https://pypi.python.org/pypi/qcref)
[![image](https://img.shields.io/pypi/l/qcref.svg)](https://pypi.python.org/pypi/qcref)
[![image](https://img.shields.io/pypi/pyversions/qcref.svg)](https://pypi.python.org/pypi/qcref)
[![CI](https://github.com/atomsforhumanity/qcref/actions/workflows/ci.yaml/badge.svg)](https://github.com/atomsforhumanity/qcref/actions/workflows/ci.yaml)

Reference data for computational chemistry: CODATA physical constants, conversion factors, a periodic table, and solvent properties, each value with its source. Lightweight and dependency-free.

- **Every value carries its source.** Each number is a `float` with `.source`, `.unit`, `.uncertainty`, and `.notes`; the package refuses to load a value without a source.
- **Data releases are versioned.** CODATA releases live side by side (`codata[2022]`), and `phys` and the curated conversion factors always follow the latest.
- **Adding data never requires code changes.** All values live in CSV files with a metadata sidecar citing their source.

> Formerly `qcconst`. `pip install qcconst` now installs `qcref` and warns on import; switch to `import qcref`.

## Data Sources

Each piece of data contains a link to its source. Primary data sources include:
| Data Name | Source | Source Links |
| -------------------- | ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Physical Constants` | NIST 2022 CODATA | [Individual Constant Lookup](http://physics.nist.gov/constants), [Fundamenal Constants Listing](https://physics.nist.gov/cuu/Constants/Table/allascii.txt), [Conversion Factors](https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b8) |
| `Periodic Table` | PubChem, IUPAC, Cordero 2008, Pyykkö 2015, Alvarez 2013 | [Periodic Table](https://pubchem.ncbi.nlm.nih.gov/periodic-table/), [Raw CSV Data](https://pubchem.ncbi.nlm.nih.gov/rest/pug/periodictable/CSV?response_type=save&response_basename=PubChemElements_all), [IUPAC Periodic Table](https://iupac.org/what-we-do/periodic-table-of-elements/), [Cordero 2008](https://doi.org/10.1039/b801115j), [Pyykkö 2015](https://doi.org/10.1021/jp5065819), [Alvarez 2013](https://doi.org/10.1039/C3DT50599E) |
| `Solvent Data` | CRC Handbook of Chemistry and Physics | Permittivity (Dielectric Constant) of Liquids, C. Wohlfarth |

## Installation

```sh
python -m pip install qcref
```

## Quickstart

Each dataset in `qcref` is a collection keyed the same way everywhere:

- Every entry has exactly one key, stored in the dataset's CSV file: `UPPER_SNAKE_CASE` for constants and solvents, the element symbol (`Ni`) for the periodic table.
- `collection.KEY` and `collection["KEY"]` are equivalent and are the only ways to look up by key.
- `collection.by_name(...)` looks an entry up by its original source name, ignoring case.
- Every value carries `.source`, `.unit`, `.uncertainty`, and `.notes`.

### Constants

```python
>>> from qcref import constants

>>> constants.BOHR_TO_ANGSTROM
0.529177210544, unit=Å, uncertainty=8.2e-11, source=CODATA 2022: https://physics.nist.gov/cuu/Constants/Table/allascii.txt, name=BOHR_TO_ANGSTROM, notes=Computed as BOHR_RADIUS * 1e10.

# Use constants just like a float
>>> constants.BOHR_TO_ANGSTROM * 10
5.29177210544

>>> constants["BOHR_TO_ANGSTROM"].source
'CODATA 2022: https://physics.nist.gov/cuu/Constants/Table/allascii.txt'

>>> constants.as_list()[:4]
['BOHR_TO_ANGSTROM', 'ANGSTROM_TO_BOHR', 'HARTREE_TO_JOULE', 'AVOGADRO_NUMBER']

# Curated constants can also be imported directly
>>> from qcref.constants import HARTREE_TO_EV
```

### All CODATA Physical Constants

Every CODATA release in the package is available as `codata[<year>]` (also `constants.codata2022`, ...). `phys` always points to the latest release, currently 2022. Keys are the `UPPER_SNAKE_CASE` form of the NIST quantity name; `by_name` accepts the NIST name itself.

```python
>>> from qcref import phys

>>> phys.SPEED_OF_LIGHT_IN_VACUUM
299792458.0, unit=m s^-1, uncertainty=0.0, source=CODATA 2022: https://physics.nist.gov/cuu/Constants/Table/allascii.txt, name=speed of light in vacuum

>>> phys.by_name("atomic unit of permittivity")
1.1126500562e-10, unit=F m^-1, uncertainty=1.7e-20, source=CODATA 2022: https://physics.nist.gov/cuu/Constants/Table/allascii.txt, name=atomic unit of permittivity
```

### Periodic Table

```python
>>> from qcref import periodic_table as pt

>>> pt.Ni
Element(symbol='Ni', number=28, name='Nickel', ...)

>>> pt["Ni"] is pt.Ni
True

>>> pt.by_name("Nickel").number
28
```

### Solvents

Solvent keys are the `UPPER_SNAKE_CASE` form of the CRC name. A leading locant is moved to the end, following the CAS index convention, so `1,4-Dioxane` is `DIOXANE_1_4`.

```python
>>> from qcref import solvents

>>> solvents.ACETONE
Solvent(name='Acetone', formula='C3H6O', dielectric=21.01, dielectric_temperature_k=293.15, ...)

>>> solvents.DIOXANE_1_4
Solvent(name='1,4-Dioxane', formula='C4H8O2', dielectric=2.2189, dielectric_temperature_k=293.15, ...)

>>> solvents.by_name("1,4-Dioxane") is solvents.DIOXANE_1_4
True

>>> solvents.ACETONE.dielectric_at(298.15)
20.49331470812499
```

The solvent dataset is generated from the CRC permittivity table. `dielectric` is the tabulated static relative permittivity, `dielectric_temperature_k` is the CRC superscript temperature converted from °C to K, and `dielectric_at(T)` evaluates the CRC polynomial fit when one is available.

## Adding New Values

All data live in CSV files under [src/qcref/data](https://github.com/atomsforhumanity/qcref/tree/master/src/qcref/data), one folder per dataset. Adding data never requires a code change:

- **New entries:** add a row to the dataset's CSV, including its `key`. Keys are `UPPER_SNAKE_CASE` (element symbols for the periodic table) and must be unique; the package refuses to import otherwise.
- **New CODATA release:** add `data/codata/<year>.csv` and `<year>.meta.json`. `phys` and every curated constant in `data/constants/constants.csv` automatically use the latest release, and older releases stay available as `codata[<year>]`.
- **New curated constants:** add a row to `data/constants/constants.csv` with an `expression` over CODATA keys or earlier rows (e.g. `BOHR_RADIUS * 1e10`). Value, uncertainty, and source are computed from the inputs.

Every CSV has a `<name>.meta.json` sidecar with a required `source` (plus optional `citation`, `notes`, and per-column `units`). Values are stored exactly as published; conversions such as Å to Bohr happen at load time and are recorded in each value's `notes`. Every loaded value must have a source.

Keys are visible to type checkers and IDEs through the generated `src/qcref/_keys.py`, so `pt.Ni` autocompletes and a mistyped key is a `mypy` error. The pre-commit hook and the build regenerate it whenever data change (or run `python build_tools/gen_keys.py`); a test fails if it is stale.

Open a PR and that's it! ✨

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup, the pre-commit workflow, running tests, and the release process.

## The QC Suite

These packages work together to make quantum chemistry fast, structured, and interoperable.

- [qcref](https://github.com/atomsforhumanity/qcref) - Reference data for computational chemistry: CODATA physical constants, conversion factors, a periodic table, and solvent properties, each value with its source.
- [qcdata](https://github.com/atomsforhumanity/qcdata) - Data structures for quantum chemistry inputs and results, with Jupyter visualizations. [Documentation](https://qcdata.docs.atomsforhumanity.org)
- [qcinf](https://github.com/atomsforhumanity/qcinf) - Cheminformatics algorithms and structure utilities for [qcdata](https://github.com/atomsforhumanity/qcdata) structures.
- [qccodec](https://github.com/atomsforhumanity/qccodec) - Translates [qcdata](https://github.com/atomsforhumanity/qcdata) inputs into native program inputs and parses program outputs back into qcdata objects, one codec per program.
- [qccompute](https://github.com/atomsforhumanity/qccompute) - Runs quantum chemistry programs on [qcdata](https://github.com/atomsforhumanity/qcdata) inputs using [qccodec](https://github.com/atomsforhumanity/qccodec) codecs and returns structured results. [Documentation](https://qccompute.docs.atomsforhumanity.org)
- [BigChem](https://github.com/mtzgroup/bigchem) - Distributed execution of qccompute calculations across clusters of computers or the cloud.
- [ChemCloud](https://github.com/mtzgroup/chemcloud-client) - A [web application](https://github.com/mtzgroup/chemcloud-server) and [Python client](https://github.com/mtzgroup/chemcloud-client) that expose a BigChem cluster securely over the internet.

