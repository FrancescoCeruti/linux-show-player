# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2018 Francesco Ceruti <ceppofrancy@gmail.com>
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

# Used to indicate the default behaviour when a specific option is not found to
# raise an exception. Created to enable `None` as a valid fallback value.
from lisp.core.singleton import ABCSingleton

_UNSET = object()

logger = logging.getLogger(__name__)


class Configuration(metaclass=ABCMeta):
    """ABC for a dictionary-based configuration object.

    Subclasses need to implement `read` and `write` methods.
    Keep in mind that the `set` and `update` methods ignores non-existing keys.
    """

    def __init__(self):
        self._root = {}
        self.changed = Signal()

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def write(self):
        pass

    def get(self, path, default=_UNSET):
        try:
            node, key = self.__traverse(path.split('.'), self._root)
            return node[key]
        except (KeyError, TypeError) as e:
            if default is not _UNSET:
                logger.warning(
                    'Invalid key "{}" in get operation, default used.'
                        .format(path)
                )
                return default

            raise e

    def set(self, path, value):
        try:
            node, key = self.__traverse(path.split('.'), self._root)
            old, node[key] = node[key], value

            self.changed.emit(path, old, value)
        except (KeyError, TypeError):
            logger.warning(
                'Invalid key "{}" in set operation, ignored.'
                    .format(path)
            )

    def __traverse(self, keys, root):
        next_step = keys.pop(0)

        if keys:
            return self.__traverse(keys, root[next_step])

        return root, next_step

    def update(self, new_conf):
        """Update the current configuration using the given dictionary.

        :param new_conf: the new configuration (can be partial)
        :type new_conf: dict
        """
        self.__update(self._root, new_conf)

    def __update(self, root, new_conf, _path=''):
        """Recursively update the current configuration."""
        for key, value in new_conf.items():
            if key in root:
                _path = self.jp(_path, key)

                if isinstance(root[key], dict):
                    self.__update(root[key], value, _path)
                else:
                    old, root[key] = root[key], value
                    self.changed.emit(_path[1:], old, value)

    def copy(self):
        """Return a deep-copy of the internal dictionary.

        :rtype: dict
        """
        return deepcopy(self._root)

    @staticmethod
    def jp(*paths):
        return '.'.join(paths)

    def __getitem__(self, path):
        return self.get(path)

    def __setitem__(self, path, value):
        self.set(path, value)

    def __contains__(self, path):
        try:
            node, key = self.__traverse(path.split('.'), self._root)
            return key in node
        except (KeyError, TypeError):
            return False


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
        with open(self.user_path, 'w') as f:
            json.dump(self._root, f, indent=True)

    def _check_file(self):
        """Ensure the last configuration is present at the user-path position"""
        if path.exists(self.user_path):
            # Read default configuration
            default = self._read_json(self.default_path)
            default = default.get('_version_', object())

            # Read user configuration
            user = self._read_json(self.user_path)
            user = user.get('_version_', object())

            # if the user and default version are the same we are good
            if user == default:
                return

        # Copy the new configuration
        copyfile(self.default_path, self.user_path)
        logger.info(
            'New configuration installed at {}'.format(self.user_path))

    @staticmethod
    def _read_json(path):
        with open(path, 'r') as f:
            return json.load(f)


# TODO: we should remove this in favor of a non-singleton
class AppConfig(JSONFileConfiguration, metaclass=ABCSingleton):
    """Provide access to the application configuration (singleton)"""

    def __init__(self):
        super().__init__(USER_APP_CONFIG, DEFAULT_APP_CONFIG)
