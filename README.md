# QCConst

[![image](https://img.shields.io/pypi/v/qcconst.svg)](https://pypi.python.org/pypi/qcconst)
[![image](https://img.shields.io/pypi/l/qcconst.svg)](https://pypi.python.org/pypi/qcconst)
[![image](https://img.shields.io/pypi/pyversions/qcconst.svg)](https://pypi.python.org/pypi/qcconst)
[![Actions status](https://github.com/coltonbh/qcconst/workflows/Tests/badge.svg)](https://github.com/coltonbh/qcconst/actions)
[![Actions status](https://github.com/coltonbh/qcconst/workflows/Basic%20Code%20Quality/badge.svg)](https://github.com/coltonbh/qcconst/actions)

Physical constants, conversion factors, solvent permittivities, and a periodic table with clear source information for every value. Data from NIST CODATA 2022, PubChem, and the CRC Handbook. All data keep source metadata alongside the numerical values.

## Data Sources

Each piece of data contains a link to its source. Primary data sources include:
| Data Name | Source | Source Links |
| -------------------- | ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Physical Constants` | NIST 2022 CODATA | [Individual Constant Lookup](http://physics.nist.gov/constants), [Fundamenal Constants Listing](https://physics.nist.gov/cuu/Constants/Table/allascii.txt), [Conversion Factors](https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b8) |
| `Periodic Table` | PubChem, Cordero 2008, Pyykkö 2009, Alvarez 2013 | [Periodic Table](https://pubchem.ncbi.nlm.nih.gov/periodic-table/), [Raw CSV Data](https://pubchem.ncbi.nlm.nih.gov/rest/pug/periodictable/CSV?response_type=save&response_basename=PubChemElements_all), [Cordero 2008](https://doi.org/10.1039/b801115j), [Pyykkö 2009](https://doi.org/10.1002/chem.200901472), [Alvarez 2013](https://doi.org/10.1039/C3DT50599E) |
| `Solvent Data` | CRC Handbook of Chemistry and Physics | `CRC Solvent Data.pdf` in the repository root |

## Installation

```sh
python -m pip install qcconst
```

## Quickstart

### Constants

Each major dataset in `qcconst` is a collection object. The package uses one primary access convention everywhere:

- attribute access uses lowercase normalized Python-safe names
- mapping access accepts canonical normalized keys and original scientific/source names where appropriate

### Constants

```python
>>> from qcconst import constants

>>> constants.bohr_to_angstrom
0.529177210544, unit=Å, uncertainty=8.2e-21, source=https://physics.nist.gov/cgi-bin/cuu/Value?bohrrada0, name=BOHR_TO_ANGSTROM

>>> constants["bohr_to_angstrom"]
0.529177210544, unit=Å, uncertainty=8.2e-21, source=https://physics.nist.gov/cgi-bin/cuu/Value?bohrrada0, name=BOHR_TO_ANGSTROM

>>> constants.bohr_to_angstrom.source
'https://physics.nist.gov/cgi-bin/cuu/Value?bohrrada0'

>>> constants.as_list()[:4]
['bohr_to_angstrom', 'angstrom_to_bohr', 'hartree_to_joule', 'avogadro_number']
```

### All CODATA Physical Constants

The full CODATA 2022 set of constants are available by their NIST-given name at `constants.phys` or `constants.codata2022`. `constants.phys` will always point to the latest CODATA values. Currently this is the 2022 release.

```python
>>> from qcconst import constants

>>> constants.phys['atomic unit of permittivity']
1.1126500562e-10, unit=kg m s^-1, source=CODATA 2022: https://physics.nist.gov/cuu/Constants/Table/allascii.txt

>>> constants.codata2022['conventional value of von Klitzing constant']
25812.807, unit=ohm, source=CODATA 2022: https://physics.nist.gov/cuu/Constants/Table/allascii.txt
```

### Periodic Table

```python
>>> from qcconst import periodic_table as pt

>>> pt.ni
Element(symbol='Ni', number=28, name='Nickel', ...)

>>> pt["ni"]
Element(symbol='Ni', number=28, name='Nickel', ...)

>>> pt.ni.symbol
'Ni'

>>> pt["Nickel"].number
28
```

### Solvents

```python
from qcconst import solvents

>>> solvents.acetone
Solvent(name='Acetone', formula='C3H6O', dielectric=21.01, dielectric_temperature_k=293.15, ...)

>>> solvents["acetone"]
Solvent(name='Acetone', formula='C3H6O', dielectric=21.01, dielectric_temperature_k=293.15, ...)

>>> solvents._1_4_dioxane
Solvent(name='1,4-Dioxane', formula='C4H8O2', dielectric=2.2189, dielectric_temperature_k=293.15, ...)

>>> solvents["1,4-Dioxane"]
Solvent(name='1,4-Dioxane', formula='C4H8O2', dielectric=2.2189, dielectric_temperature_k=293.15, ...)

>>> solvents.acetone.dielectric
21.01

>>> solvents.acetone.dielectric_temperature_k
293.15

>>> solvents.acetone.dielectric_at(298.15)
20.49331470812499
```

The solvent dataset is generated from the CRC permittivity table. `dielectric` is the tabulated static relative permittivity, `dielectric_temperature_k` is the CRC superscript temperature converted from °C to K, and `dielectric_at(T)` evaluates the CRC polynomial fit when one is available.

## Adding New Values

Adding new values is simple! Just add it to one of the `.csv` files in [src/qcconst/data](https://github.com/coltonbh/qcconst/tree/master/src/qcconst/data). Include the value, its source, and any other required metadata and then open a PR. That's it! ✨

## The QC Suite of Programs

If you like `qcconst` you may like my other libraries for computational chemistry.

- [qcio](https://github.com/coltonbh/qcio) - Elegant and intuitive data structures for quantum chemistry, featuring seamless Jupyter Notebook visualizations. [Documentation](https://qcio.coltonhicks.com)
- [qccodec](https://github.com/coltonbh/qccodec) - A library for parsing Quantum Chemistry output files into structured data objects and converting structured input objects into program-native input files. Uses data structures from `qcio`.
- [qcop](https://github.com/coltonbh/qcop) - A package for operating quantum chemistry programs using `qcio` standardized data structures. Compatible with `TeraChem`, `psi4`, `QChem`, `NWChem`, `ORCA`, `Molpro`, `geomeTRIC` and many more.
- [BigChem](https://github.com/mtzgroup/bigchem) - A distributed application for running quantum chemistry calculations at scale across clusters of computers or the cloud. Bring multi-node scaling to your favorite quantum chemistry program.
- `ChemCloud` - A [web application](https://github.com/mtzgroup/chemcloud-server) and associated [Python client](https://github.com/mtzgroup/chemcloud-client) for exposing a BigChem cluster securely over the internet.
