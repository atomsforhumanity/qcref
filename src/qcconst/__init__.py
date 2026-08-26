from importlib import metadata as _metadata

try:
    __version__ = _metadata.version(__name__)
except _metadata.PackageNotFoundError:
    # Source tree / build hook / CI checkout
    __version__ = "0.0.0+local"

from .constants import constants, phys  # noqa: F401
from .periodic_table import PeriodicTable, periodic_table  # noqa: F401
from .solvents import solvents  # noqa: F401
