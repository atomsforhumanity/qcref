from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import asdict, is_dataclass
from typing import Callable, Generic, TypeVar

from .utils import to_table

T = TypeVar("T")

_NON_IDENTIFIER_CHARS = re.compile(r"[\s,\-./()]+")
_REPEATED_UNDERSCORES = re.compile(r"_+")


def normalize_name(name: str) -> str:
    """Normalize a scientific/source name into a lowercase Python-safe alias."""
    normalized = _NON_IDENTIFIER_CHARS.sub("_", name.strip().lower())
    normalized = _REPEATED_UNDERSCORES.sub("_", normalized).strip("_")
    if normalized and normalized[0].isdigit():
        normalized = f"_{normalized}"
    if not normalized.isidentifier():
        normalized = re.sub(r"[^0-9a-zA-Z_]", "_", normalized)
        normalized = _REPEATED_UNDERSCORES.sub("_", normalized).strip("_")
        if normalized and normalized[0].isdigit():
            normalized = f"_{normalized}"
    if not normalized or not normalized.isidentifier():
        raise ValueError(f"Cannot normalize {name!r} into a valid identifier.")
    return normalized


class NamedCollection(Generic[T], Mapping[str, T]):
    """Mapping-like collection with normalized attribute aliases."""

    def __init__(
        self,
        entries: Iterable[T],
        *,
        source_name: Callable[[T], str],
        canonical_key: Callable[[T], str] | None = None,
        aliases: Callable[[T], Iterable[str]] | None = None,
    ) -> None:
        self._items_by_key: dict[str, T] = {}
        self._source_names: dict[str, str] = {}
        self._aliases_by_key: dict[str, set[str]] = {}
        self._alias_to_keys: dict[str, set[str]] = {}
        self._lookup_by_casefold: dict[str, str] = {}

        for entry in entries:
            source = source_name(entry)
            key = canonical_key(entry) if canonical_key else normalize_name(source)
            if key in self._items_by_key:
                self._disambiguate_existing_key(key)
                key = self._make_unique_key(key)

            self._items_by_key[key] = entry
            self._source_names[key] = source

            entry_aliases = {key, normalize_name(source)}
            if aliases:
                entry_aliases.update(normalize_name(alias) for alias in aliases(entry))
            self._aliases_by_key[key] = entry_aliases

            self._lookup_by_casefold[key.casefold()] = key
            self._lookup_by_casefold[source.casefold()] = key
            for alias in entry_aliases:
                self._alias_to_keys.setdefault(alias, set()).add(key)

    def _make_unique_key(self, base_key: str) -> str:
        counter = 2
        while f"{base_key}_{counter}" in self._items_by_key:
            counter += 1
        return f"{base_key}_{counter}"

    def _disambiguate_existing_key(self, base_key: str) -> None:
        if f"{base_key}_1" in self._items_by_key:
            return

        existing_item = self._items_by_key.pop(base_key)
        existing_source = self._source_names.pop(base_key)
        existing_aliases = self._aliases_by_key.pop(base_key)
        self._lookup_by_casefold.pop(base_key.casefold(), None)

        new_key = f"{base_key}_1"
        self._items_by_key[new_key] = existing_item
        self._source_names[new_key] = existing_source
        updated_aliases = {new_key, *existing_aliases}
        self._aliases_by_key[new_key] = updated_aliases
        self._lookup_by_casefold[new_key.casefold()] = new_key
        self._lookup_by_casefold[existing_source.casefold()] = new_key
        self._alias_to_keys.setdefault(new_key, set()).add(new_key)

        for alias, keys in self._alias_to_keys.items():
            if base_key in keys:
                keys.remove(base_key)
                keys.add(new_key)

    def _resolve(self, name: str) -> str:
        if name in self._items_by_key:
            return name

        stripped = name.strip()
        direct_match = self._lookup_by_casefold.get(stripped.casefold())
        if direct_match is not None:
            return direct_match

        try:
            normalized = normalize_name(stripped)
        except ValueError as exc:
            raise KeyError(name) from exc
        if normalized in self._items_by_key:
            return normalized

        alias_matches = self._alias_to_keys.get(normalized, set())
        if len(alias_matches) == 1:
            return next(iter(alias_matches))
        if len(alias_matches) > 1:
            matches = ", ".join(sorted(alias_matches))
            raise KeyError(f"{name!r} is ambiguous; matches canonical keys: {matches}")
        raise KeyError(name)

    def __getitem__(self, key: str) -> T:
        return self._items_by_key[self._resolve(key)]

    def get(self, key: str, default: T | None = None) -> T | None:
        try:
            return self[key]
        except KeyError:
            return default

    def __getattr__(self, name: str) -> T:
        alias_matches = self._alias_to_keys.get(name, set())
        if len(alias_matches) == 1:
            return self._items_by_key[next(iter(alias_matches))]
        raise AttributeError(f"{type(self).__name__!s} has no attribute {name!r}")

    def __iter__(self) -> Iterator[str]:
        return iter(self._items_by_key)

    def __len__(self) -> int:
        return len(self._items_by_key)

    def __dir__(self) -> list[str]:
        clean_aliases = [
            alias
            for alias, keys in self._alias_to_keys.items()
            if len(keys) == 1 and alias.isidentifier()
        ]
        return sorted(set(clean_aliases))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({len(self)} entries)"

    def as_list(self) -> list[str]:
        return list(self._items_by_key)

    def canonical_key(self, name: str) -> str:
        return self._resolve(name)

    def source_name(self, name: str) -> str:
        return self._source_names[self._resolve(name)]

    def aliases_for(self, name: str) -> list[str]:
        key = self._resolve(name)
        return sorted(self._aliases_by_key[key])

    def show(self) -> None:
        rows = []
        for key, item in self._items_by_key.items():
            if is_dataclass(item):
                row = asdict(item)
            elif hasattr(item, "__dict__"):
                row = dict(vars(item))
            else:
                row = {"value": item}
            row = {"key": key, **row}
            rows.append(row)
        to_table(rows)
