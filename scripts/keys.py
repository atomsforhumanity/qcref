"""Generate UPPER_SNAKE_CASE keys from scientific names.

Used by data-extraction scripts to *propose* keys. Keys are stored in the CSV
files and may be hand-edited afterwards; the package never derives keys at
runtime.

Rules:
    - Greek letters are spelled out (α -> ALPHA).
    - The racemic marker "(±)" is dropped.
    - A leading locant group ("1,4-", "2H-") is moved to the end, following the
      CAS index convention ("1,4-Dioxane" -> "DIOXANE_1_4").
    - Every other run of non-alphanumeric characters becomes a single "_".
"""

from __future__ import annotations

import keyword
import re

_GREEK = {
    "α": "alpha",
    "β": "beta",
    "γ": "gamma",
    "δ": "delta",
    "ε": "epsilon",
    "ω": "omega",
}
_LEADING_LOCANTS = re.compile(r"^\(?(\d+[A-Za-z]?(?:,\d+[A-Za-z]?)*)[-\s]")
_NON_ALNUM = re.compile(r"[^0-9A-Za-z]+")


def make_key(name: str) -> str:
    """Propose an UPPER_SNAKE_CASE key for a scientific name."""
    text = name.replace("(±)", "")
    for letter, spelled in _GREEK.items():
        text = text.replace(letter, f"{spelled}-")
    text = text.strip(" ,-")

    locants: list[str] = []
    while match := _LEADING_LOCANTS.match(text):
        locants.append(match.group(1))
        text = text[match.end() :]

    key = _NON_ALNUM.sub("_", " ".join([text, *locants])).strip("_").upper()
    if not is_valid_key(key):
        raise ValueError(f"Cannot make a valid key from {name!r} (got {key!r}).")
    return key


def is_valid_key(key: str) -> bool:
    return key.isidentifier() and not keyword.iskeyword(key)
