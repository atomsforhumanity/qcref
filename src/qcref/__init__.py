"""Reference data for quantum chemistry.

Physical constants (`constants`, `phys`, `codata`), the periodic table
(`periodic_table`), solvent permittivities (`solvents`), and the settings DFTB
parameter sets prescribe (`dftb_parameter_sets`), each value carrying its unit
and source.
"""

from importlib import metadata as _metadata

try:
    __version__ = _metadata.version(__name__)
except _metadata.PackageNotFoundError:
    # Source tree / build hook / CI checkout
    __version__ = "0.0.0+local"

from .constants import codata, constants, phys  # noqa: F401
from .dftb import dftb_parameter_sets  # noqa: F401
from .periodic_table import PeriodicTable, periodic_table  # noqa: F401
from .solvents import solvents  # noqa: F401
