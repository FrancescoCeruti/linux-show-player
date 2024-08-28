from copy import deepcopy

from lisp.core.util import typename, dict_merge

_UNSET = object()
"""Used to indicate the default behaviour when a specific option is not found to
raise an exception. Created to enable `None` as a valid fallback value."""


class NestedDictError(Exception):
    pass


class NestedDict:
    """Allow to access nested values using dot notation."""

    def __init__(self, root: dict | None = None, separator: str = "."):
        if not isinstance(separator, str):
            raise TypeError(
                f"{typename(self)} separator must be a str, not {typename(separator)}"
            )
        if not separator:
            raise ValueError(f"{typename(self)} separator cannot be empty")

        self._seperator = separator

        if root is None:
            self._root = {}
        elif isinstance(root, dict):
            self._root = root
        else:
            raise TypeError(
                f"{typename(self)}  root must be a dict, not {typename(root)}"
            )

    def get(self, key: str, default=_UNSET):
        try:
            node, key = self.__traverse(self.sp(key), self._root)
            return node[key]
        except (KeyError, TypeError):
            if default is not _UNSET:
                return default

            raise NestedDictError("invalid path")

    def set(self, key: str, value):
        try:
            node, key = self.__traverse(
                self.sp(key), self._root, create_missing=True
            )
            if node.get(key, _UNSET) != value:
                node[key] = value
                return True

            return False
        except (KeyError, TypeError):
            raise NestedDictError("invalid path")

    def pop(self, key: str):
        try:
            node, key = self.__traverse(self.sp(key), self._root)
            return node.pop(key)
        except (KeyError, TypeError):
            raise NestedDictError("invalid path")

    def move(self, current_key: str, new_key: str):
        self.set(new_key, self.pop(current_key))

    def update(self, other):
        """Deep update using the given dictionary.

        :param other: a dict containing the new values
        :type other: dict
        """
        dict_merge(self._root, deepcopy(other))

    def deep_copy(self) -> dict:
        """Return a deep-copy of the internal dictionary."""
        return deepcopy(self._root)

    def jp(self, *paths: str) -> str:
        return self._seperator.join(paths)

    def sp(self, key: str) -> list[str]:
        return key.split(self._seperator)

    def __traverse(self, keys: list, root: dict, create_missing: bool = False):
        next_step = keys.pop(0)

        if keys:
            if create_missing and next_step not in root:
                root[next_step] = {}

            return self.__traverse(keys, root[next_step])

        return root, next_step

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        self.pop(key)

    def __contains__(self, key):
        try:
            node, key = self.__traverse(self.sp(key), self._root)
            return key in node
        except (KeyError, TypeError):
            return False
