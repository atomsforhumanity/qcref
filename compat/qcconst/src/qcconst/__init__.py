"""Deprecated alias for `qcref`, the new name of this package."""

import sys
import warnings

import qcref
from qcref import *  # noqa: F403

warnings.warn(
    "qcconst has been renamed to qcref. Run `pip install qcref` and use "
    "`import qcref` instead; this alias will receive no further updates.",
    DeprecationWarning,
    stacklevel=2,
)

# Make `qcconst.<submodule>` (e.g. `from qcconst.constants import X`) resolve to
# the matching, already-imported qcref module.
for _name, _module in list(sys.modules.items()):
    if _name.startswith("qcref."):
        sys.modules[f"qcconst{_name[len('qcref') :]}"] = _module

__version__ = qcref.__version__
