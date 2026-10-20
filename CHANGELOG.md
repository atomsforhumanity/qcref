# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

### Changed

- The README's Data Sources table lists the DFTB parameter sets.

## [0.4.0] - 2026-10-20

### Added

- `dftb_parameter_sets`: the settings DFTB Slater-Koster parameter sets prescribe for their use, keyed `OB3_3_1` and `MIO_1_1` (or `by_name("3ob-3-1")`). Each set records its model (DFTB3 or SCC-DFTB), release, download URL, license, the citation its license requires, the H-bond damping exponent (3ob), and per-element maximum angular momenta and DFTB3 Hubbard derivatives. Values come from each set's release in the dftbparams GitHub repositories; the Slater-Koster files themselves are not included.

### Changed

- Development tooling: shared ruff (including Google docstring rules), mypy (fully typed library code), and pytest settings; pre-commit hooks that run the locked tools through `uv run`; one CI workflow; a tag-driven release workflow with `scripts/prepare_release.py` and an approval-gated PyPI deployment. Added CONTRIBUTING.md and AGENTS.md.

## [0.3.0] - 2026-10-14

### Changed

- 🚨 Renamed the package from `qcconst` to `qcref`. A final `qcconst` 0.3.0 release (in `compat/qcconst/`) installs `qcref`, re-exports it, and emits a `DeprecationWarning`.
- 🚨 Every entry has exactly one key, stored in its CSV: `UPPER_SNAKE_CASE` for constants, CODATA, and solvents; the element symbol for the periodic table. `x.KEY` and `x["KEY"]` are equivalent. Look up by source name with `by_name()` (e.g. `phys.by_name("speed of light in vacuum")`, `pt.by_name("Nickel")`); `phys["<NIST name>"]` no longer works.
- 🚨 Solvent data now come from the CRC Handbook (106th ed.) permittivity table, with temperature fits via `Solvent.dielectric_at(T)`. Solvent keys move leading locants to the end (`1,4-Dioxane` -> `DIOXANE_1_4`).
- 🚨 `PeriodicTable.group()`/`.period()` raise `ValueError` instead of `AssertionError`.
- 🚨 Requires Python 3.10+.
- Curated constants are computed from the latest CODATA release (`data/constants/constants.csv` expressions), with propagated uncertainties.
- Pyykkö radii are cited to the 2015 summary: <https://doi.org/10.1021/jp5065819>.
- Data are stored as published (Å, pm) and converted to Bohr at load time; conversions are recorded in each value's `notes`.

### Added

- Every dataset has a `.meta.json` sidecar with a required `source`; `Value` refuses an empty source.
- `codata[year]` mapping of all CODATA releases found in `data/codata/`; `phys` is the latest.
- `Element.cov_radius_single` (Pyykkö 2015 single-bond radii).
- `Collection.by_name()` lookup by original source name.
- Typed key declarations (`_keys.py`, generated from the data) so IDEs autocomplete keys and `mypy` flags mistyped ones.

### Fixed

- `BOHR_TO_ANGSTROM` uncertainty was in meters (8.2e-21) instead of Å (8.2e-11).
- `ANGSTROM_TO_BOHR` and `EV_TO_HARTREE` copied the absolute uncertainty of their inverses instead of propagating it.

### Removed

- `constants.pyi` stub (replaced by generated key declarations).

## [0.2.2] - 2026-08-26

- Updated GitHub references from `coltonbh` to `atomsforhumanity`.

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

[unreleased]: https://github.com/atomsforhumanity/qcref/compare/0.4.0...HEAD
[0.4.0]: https://github.com/atomsforhumanity/qcref/releases/tag/0.4.0
[0.3.0]: https://github.com/atomsforhumanity/qcref/releases/tag/0.3.0
[0.2.2]: https://github.com/atomsforhumanity/qcref/releases/tag/0.2.2
[0.2.1]: https://github.com/atomsforhumanity/qcref/releases/tag/0.2.1
[0.2.0]: https://github.com/atomsforhumanity/qcref/releases/tag/0.2.0
[0.1.2]: https://github.com/atomsforhumanity/qcref/releases/tag/0.1.2
[0.1.1]: https://github.com/atomsforhumanity/qcref/releases/tag/0.1.1
[0.1.0]: https://github.com/atomsforhumanity/qcref/releases/tag/0.1.0
