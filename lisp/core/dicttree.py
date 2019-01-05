# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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

# Used to indicate the default behaviour when a specific option is not found to
# raise an exception. Created to enable `None` as a valid fallback value.
from lisp.core.util import typename

_UNSET = object()


class DictTreeError(Exception):
    pass


class DictNode:
    Sep = "."

    def __init__(self, value=None, parent=None):
        self.parent = parent
        self.value = value
        self.name = None

        self._children = {}

    @property
    def children(self):
        return self._children.values()

    def add_child(self, node, name):
        if not isinstance(node, DictNode):
            raise TypeError(
                "DictNode children must be a DictNode, not {}".format(
                    typename(node)
                )
            )
        if not isinstance(name, str):
            raise TypeError(
                "DictNode name must be a str, not {}".format(typename(node))
            )
        if self.Sep in name:
            raise DictTreeError(
                "DictNode name cannot contains the path separator"
            )

        # Set node name and parent
        node.name = name
        node.parent = self
        # Add the node to the children dictionary
        self._children[name] = node

    def get(self, path, default=_UNSET):
        if isinstance(path, str):
            path = self.sp(path)

        try:
            child_key = path.pop(0)
            if path:
                return self._children[child_key].get(path, default=default)

            return self._children[child_key].value
        except (KeyError, TypeError):
            if default is not _UNSET:
                return default

            raise DictTreeError("invalid path")

    def set(self, path, value):
        if isinstance(path, str):
            path = self.sp(path)

        try:
            child_key = path.pop(0)
            if child_key not in self._children:
                self.add_child(DictNode(), child_key)

            if path:
                self._children[child_key].set(path, value)
            else:
                self._children[child_key].value = value
        except (KeyError, TypeError):
            raise DictTreeError("invalid path")

    def pop(self, path):
        if isinstance(path, str):
            path = self.sp(path)

        try:
            child_key = path.pop(0)
            if path:
                self._children[child_key].pop(path)
            else:
                self._children.pop(child_key)
        except (KeyError, TypeError):
            raise DictTreeError("Invalid path")

    def path(self):
        if self.parent is not None:
            pp = self.parent.path()
            if pp:
                return self.jp(pp, self.name)
            else:
                return self.name

        return ""

    @classmethod
    def jp(cls, *paths):
        return cls.Sep.join(paths)

    @classmethod
    def sp(cls, path):
        return path.split(cls.Sep)

    def __getitem__(self, path):
        return self.get(path)

    def __setitem__(self, path, value):
        self.set(path, value)

    def __delitem__(self, path):
        self.pop(path)

    def __contains__(self, path):
        try:
            path = self.sp(path)
            child_key = path.pop(0)
            if path:
                return path in self._children[child_key]

            return child_key in self._children
        except (KeyError, TypeError):
            return False
