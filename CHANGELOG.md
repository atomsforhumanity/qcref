# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

## [0.2.1] - 2025-05-31

### Added

- `hatchling` build hook to autogenerate a `constants.pyi` stub file so static checking (`mypy`) can pass in other repos that use `constants.SOME_VALUE`.
- Fallback value to package `version` in `__init__.py`. Needed for running build scripts since the repo isn't "installed" yet and this lookup using `metadata.version()` fails.

## [0.2.0] - 2025-05-01

### Added

- Added all `CODATA 2022` values at `constants.codata2022` as a dictionary with keys corresponding to the `CODATA 2022` names given at https://physics.nist.gov/cuu/Constants/Table/allascii.txt.
- `constants.phys` points to the latest CODATA release (currently 2022).
- Covalent radii for elements from Cordero et. al. 2008: <https://doi.org/10.1039/b801115j>.
- van der Waals radii from Alvarez 2013: <https://doi.org/10.1039/C3DT50599E>.
- Atomic radii from the existing PubChem data <https://pubchem.ncbi.nlm.nih.gov/periodic-table>.
- Electronegativity from the existing PubChem data <https://pubchem.ncbi.nlm.nih.gov/periodic-table>.
- Double and triple bond covalent radii from Pyykkö <https://doi.org/10.1002/chem.200901472>.

### Changed

- 🚨 Renamed `Atom` -> `Element`.

### Removed

- `tabulate` dependency in favor or internal `_tabulate()` function.

## [0.1.2] - 2025-04-01

### Changed

- GitHub workflows now trigger on `pull_request` and only pushes to `master`.
- Version update in `release.py` now happens with `re` package rather than `poetry`.
- Added `write` permission to `create-release.yaml` GitHub action.

## [0.1.1] - 2025-03-24

### Added

- `constants.HARTREE_TO_EV` and `constants.EV_TO_HARTREE`.

## [0.1.0] - 2025-03-21

### Added

- Core physical constants, periodic table, and solvent properties.
- Common API for showing available constants and solvents.

[unreleased]: https://github.com/atomsforhumanity/qcconst/compare/0.2.1...HEAD
[0.2.1]: https://github.com/atomsforhumanity/qcconst/releases/tag/0.2.1
[0.2.0]: https://github.com/atomsforhumanity/qcconst/releases/tag/0.2.0
[0.1.2]: https://github.com/atomsforhumanity/qcconst/releases/tag/0.1.2
[0.1.1]: https://github.com/atomsforhumanity/qcconst/releases/tag/0.1.1
[0.1.0]: https://github.com/atomsforhumanity/qcconst/releases/tag/0.1.0
