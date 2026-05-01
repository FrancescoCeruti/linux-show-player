# This file is part of Linux Show Player
#
# Copyright 2024 Francesco Ceruti <ceppofrancy@gmail.com>
#
# Linux Show Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linux Show Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>.

from collections.abc import MutableMapping
from copy import deepcopy

from lisp.core.util import dict_merge, typename

_UNSET = object()
"""A sentinel object indicating no default, allows the use of `None` as a default value."""


class PathError(KeyError):
    pass


class DotDict(MutableMapping):
    """Wrapper that allows using dot notation to access nested values."""

    def __init__(self, root: dict | None = None, separator: str = "."):
        if not isinstance(separator, str):
            raise TypeError(
                f"{typename(self)} separator must be a str, not {typename(separator)}"
            )
        if not separator:
            raise ValueError(f"{typename(self)} separator cannot be empty")

        self._separator = separator

        if root is None:
            self._root = {}
        elif isinstance(root, dict):
            self._root = root
        else:
            raise TypeError(
                f"{typename(self)} root must be a dict, not {typename(root)}"
            )

    def get(self, key: str, default=_UNSET):
        try:
            node, last_key = self.__traverse(self.sp(key), self._root)
            return node[last_key]
        except (KeyError, TypeError):
            if default is not _UNSET:
                return default

            raise PathError(key) from None

    def set(self, key: str, value):
        try:
            node, last_key = self.__traverse(
                self.sp(key), self._root, create_missing=True
            )
            if node.get(last_key, _UNSET) != value:
                node[last_key] = value
                return True

            return False
        except (KeyError, TypeError):
            raise PathError(key) from None

    def pop(self, key: str):
        try:
            node, last_key = self.__traverse(self.sp(key), self._root)
            return node.pop(last_key)
        except (KeyError, TypeError):
            raise PathError(key) from None

    def move(self, current_key: str, new_key: str):
        self.set(new_key, self.pop(current_key))

    def update(self, other: dict):
        """Deep update using the given dictionary."""
        dict_merge(self._root, deepcopy(other))

    def deep_copy(self) -> dict:
        """Return a deep-copy of the internal dictionary."""
        return deepcopy(self._root)

    def jp(self, *paths: str) -> str:
        return self._separator.join(paths)

    def sp(self, key: str) -> list[str]:
        return key.split(self._separator)

    def __traverse(self, keys: list, root: dict, create_missing: bool = False):
        next_step = keys.pop(0)

        if len(keys) == 0:
            return root, next_step

        if create_missing and next_step not in root:
            root[next_step] = {}

        return self.__traverse(keys, root[next_step])

    def __iter__(self):
        return self._root.__iter__()

    def __len__(self):
        return self._root.__len__()

    def __getitem__(self, key: str):
        return self.get(key)

    def __setitem__(self, key: str, value):
        self.set(key, value)

    def __delitem__(self, key: str):
        self.pop(key)

    def __contains__(self, key: str):
        try:
            node, key = self.__traverse(self.sp(key), self._root)
            return key in node
        except (KeyError, TypeError):
            return False
