import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_generated_keys_are_up_to_date():
    spec = importlib.util.spec_from_file_location(
        "gen_keys", ROOT / "build_tools" / "gen_keys.py"
    )
    gen_keys = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen_keys)
    assert gen_keys.OUTPUT.read_text(encoding="utf-8") == gen_keys.render(), (
        "src/qcconst/_keys.py is stale; run: python build_tools/gen_keys.py"
    )
