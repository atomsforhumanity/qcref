from __future__ import annotations

import keyword
import re
from collections.abc import Iterable, Iterator, Mapping
from typing import Any, Callable, ClassVar, Generic, TypeVar

from .utils import to_table

T = TypeVar("T")


class Collection(Generic[T], Mapping[str, T]):
    """Read-only mapping of reference data entries.

    Every entry has exactly one key, stored in the dataset's CSV file. ``c.KEY`` and
    ``c["KEY"]`` are equivalent. ``c.by_name(...)`` looks an entry up by its
    original (source) name instead, ignoring case.
    """

    key_pattern: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Z][A-Z0-9_]*$")

    def __init__(
        self, entries: Iterable[tuple[str, T]], *, name_of: Callable[[T], str]
    ) -> None:
        self._entries: dict[str, T] = {}
        self._keys_by_name: dict[str, str] = {}
        for key, entry in entries:
            self._validate_key(key)
            self._entries[key] = entry
            name = name_of(entry).casefold()
            if name in self._keys_by_name:
                raise ValueError(
                    f"Duplicate name {name_of(entry)!r} for keys "
                    f"{self._keys_by_name[name]!r} and {key!r}."
                )
            self._keys_by_name[name] = key

    def _validate_key(self, key: str) -> None:
        if key in self._entries:
            raise ValueError(f"Duplicate key {key!r}.")
        if (
            not self.key_pattern.fullmatch(key)
            or keyword.iskeyword(key)
            or hasattr(type(self), key)
        ):
            raise ValueError(f"Invalid key {key!r} for {type(self).__name__}.")

    def __getitem__(self, key: str) -> T:
        return self._entries[key]

    def __getattr__(self, key: str) -> T:
        try:
            return self.__dict__["_entries"][key]
        except KeyError:
            raise AttributeError(
                f"{type(self).__name__!s} has no attribute {key!r}"
            ) from None

    def __iter__(self) -> Iterator[str]:
        return iter(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __dir__(self) -> list[str]:
        return sorted(set(super().__dir__()) | set(self._entries))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({len(self)} entries)"

    def as_list(self) -> list[str]:
        """Return all keys in dataset order."""
        return list(self._entries)

    def by_name(self, name: str) -> T:
        """Return the entry whose original (source) name matches, ignoring case."""
        try:
            return self._entries[self._keys_by_name[name.casefold()]]
        except KeyError:
            raise KeyError(name) from None

    def show(self) -> None:
        """Print a human-readable table of all entries."""
        to_table([{"key": key, **self._row(entry)} for key, entry in self.items()])

    def _row(self, entry: T) -> dict[str, Any]:
        return {"value": entry}
