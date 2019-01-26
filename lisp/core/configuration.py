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
# raise an exception. Created to enable `None' as a valid fallback value.

import json
import logging
from abc import ABCMeta, abstractmethod
from copy import deepcopy
from os import path
from shutil import copyfile

from lisp import DEFAULT_APP_CONFIG, USER_APP_CONFIG
from lisp.core.signal import Signal
from lisp.core.singleton import ABCSingleton
from lisp.core.util import dict_merge, dict_merge_diff, typename
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)

_UNSET = object()


class ConfDictError(Exception):
    pass


class ConfDict:
    """Allow to access nested-dictionaries values using "paths"."""

    def __init__(self, root=None, sep="."):
        if not sep:
            raise ValueError("ConfDict separator cannot be empty")
        if not isinstance(sep, str):
            raise TypeError(
                "ConfDict separator must be a str, not {}".format(typename(sep))
            )

        self._sep = sep

        if root is None:
            self._root = {}
        elif isinstance(root, dict):
            self._root = root
        else:
            raise TypeError(
                "ConfDict root must be a dict, not {}".format(typename(root))
            )

    def get(self, path, default=_UNSET):
        try:
            node, key = self.__traverse(self.sp(path), self._root)
            return node[key]
        except (KeyError, TypeError):
            if default is not _UNSET:
                logger.info(
                    translate(
                        "ConfigurationInfo",
                        'Invalid path "{}", return default.',
                    ).format(path)
                )
                return default

            raise ConfDictError("invalid path")

    def set(self, path, value):
        try:
            node, key = self.__traverse(self.sp(path), self._root, set_=True)
            if node.get(key, _UNSET) != value:
                node[key] = value
                return True

            return False
        except (KeyError, TypeError):
            raise ConfDictError("invalid path")

    def pop(self, path):
        try:
            node, key = self.__traverse(self.sp(path), self._root)
            return node.pop(key)
        except (KeyError, TypeError):
            raise ConfDictError("invalid path")

    def update(self, new_conf):
        """Update the ConfDict using the given dictionary.

        :param new_conf: a dict containing the new values
        :type new_conf: dict
        """
        dict_merge(self._root, deepcopy(new_conf))

    def deep_copy(self):
        """Return a deep-copy of the internal dictionary."""
        return deepcopy(self._root)

    def jp(self, *paths):
        return self._sep.join(paths)

    def sp(self, path):
        return path.split(self._sep)

    def __traverse(self, keys, root, set_=False):
        next_step = keys.pop(0)

        if keys:
            if set_ and next_step not in root:
                root[next_step] = {}

            return self.__traverse(keys, root[next_step])

        return root, next_step

    def __getitem__(self, path):
        return self.get(path)

    def __setitem__(self, path, value):
        self.set(path, value)

    def __delitem__(self, path):
        self.pop(path)

    def __contains__(self, path):
        try:
            node, key = self.__traverse(path.split(self._sep), self._root)
            return key in node
        except (KeyError, TypeError):
            return False


class Configuration(ConfDict, metaclass=ABCMeta):
    """ABC for configuration objects.

    Subclasses need to implement `read` and `write` methods.
    """

    def __init__(self, root=None):
        super().__init__(root=root)
        self.changed = Signal()
        self.updated = Signal()

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def write(self):
        pass

    def set(self, path, value):
        changed = super().set(path, value)
        if changed:
            self.changed.emit(path, value)

        return changed

    def update(self, new_conf):
        diff = dict_merge_diff(self._root, new_conf)
        if diff:
            super().update(diff)
            self.updated.emit(diff)


class DummyConfiguration(Configuration):
    """Configuration without read/write capabilities."""

    def read(self):
        pass

    def write(self):
        pass


class JSONFileConfiguration(Configuration):
    """Read/Write configurations from/to a JSON file.

    Two path must be provided on creation, user-path and default-path,
    the first one is used to read/write, the second is copied over when the
    first is not available or the version value is different.

    While the default-path can (and should) be read-only, the user-path must
    be writeable by the application.

    The version value should be located at "_version_", the value can be
    anything. If the default and user value are different or missing the default
    configuration is copied over.
    """

    def __init__(self, user_path, default_path, read=True):
        super().__init__()

        self.user_path = user_path
        self.default_path = default_path

        if read:
            self.read()

    def read(self):
        self._check_file()
        self._root = self._read_json(self.user_path)

    def write(self):
        with open(self.user_path, "w") as f:
            json.dump(self._root, f, indent=True)

        logger.debug(
            translate(
                "ConfigurationDebug", "Configuration written at {}"
            ).format(self.user_path)
        )

    def _check_file(self):
        """Ensure the last configuration is present at the user-path position"""
        if path.exists(self.user_path):
            # Read default configuration
            default = self._read_json(self.default_path)
            default = default.get("_version_", object())

            # Read user configuration
            user = self._read_json(self.user_path)
            user = user.get("_version_", object())

            # if the user and default version are the same we are good
            if user == default:
                return

        # Copy the new configuration
        copyfile(self.default_path, self.user_path)
        logger.info(
            translate(
                "ConfigurationInfo", "New configuration installed at {}"
            ).format(self.user_path)
        )

    @staticmethod
    def _read_json(path):
        with open(path, "r") as f:
            return json.load(f)


class AppConfig(JSONFileConfiguration, metaclass=ABCSingleton):
    """Provide access to the application configuration (singleton)"""

    def __init__(self):
        super().__init__(USER_APP_CONFIG, DEFAULT_APP_CONFIG)
