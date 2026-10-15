# Hatch build hook – executed automatically when running `uv build`
# Regenerates src/qcref/_keys.py (typed key declarations) from the CSV data.
import subprocess
import sys
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.plugin import hookimpl


class KeysGenHook(BuildHookInterface):
    def initialize(self, version, build_data):
        gen = Path(__file__).with_name("gen_keys.py")
        subprocess.check_call([sys.executable, str(gen)])


@hookimpl
def hatch_register_build_hook():
    return KeysGenHook
