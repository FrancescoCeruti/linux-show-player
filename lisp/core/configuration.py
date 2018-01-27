# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2017 Francesco Ceruti <ceppofrancy@gmail.com>
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

from collections import Mapping
from os import path
from shutil import copyfile

import json

from lisp.core.util import deep_update

from lisp import USER_APP_CONFIG, DEFAULT_APP_CONFIG
from lisp.core.singleton import Singleton

# Used to indicate the default behaviour when a specific option is not found to
# raise an exception. Created to enable `None' as a valid fallback value.
_UNSET = object()


# TODO: HasProperties?
class Configuration:
    """Allow to read/write json based configuration files.

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
        self.__config = {}

        self.user_path = user_path
        self.default_path = default_path

        if read:
            self.read()

    def read(self):
        self.check()
        self.__config = self._read_json(self.user_path)

    def write(self):
        with open(self.user_path, 'w') as f:
            json.dump(self.__config, f, indent=True)

    def check(self):
        if path.exists(self.user_path):
            # Read default configuration
            default = self._read_json(self.default_path)
            default = default.get('_version_', object())

            # Read user configuration
            user = self._read_json(self.user_path)
            user = user.get('_version_', object())

            # if the user and default version aren't the same
            if user != default:
                # Copy the new configuration
                copyfile(self.default_path, self.user_path)
        else:
            copyfile(self.default_path, self.user_path)

    @staticmethod
    def _read_json(path):
        with open(path, 'r') as f:
            return json.load(f)

    def get(self, *path, default=_UNSET):
        value = self.__config
        for key in path:
            if isinstance(value, Mapping):
                try:
                    value = value[key]
                except KeyError:
                    if default is _UNSET:
                        raise
                    return default
            else:
                break

        return value

    def copy(self):
        return self.__config.copy()

    def update(self, update_dict):
        deep_update(self.__config, update_dict)

    def __getitem__(self, item):
        return self.__config.__getitem__(item)

    def __setitem__(self, key, value):
        return self.__config.__setitem__(key, value)

    def __contains__(self, key):
        return self.__config.__contains__(key)


class DummyConfiguration(Configuration):
    """Configuration without read/write capabilities.

    Can be used for uninitialized component.
    """

    def __init__(self):
        super().__init__('', '', False)

    def read(self):
        pass

    def write(self):
        pass

    def check(self):
        pass


# TODO: we should remove this in favor of a non-singleton
class AppConfig(Configuration, metaclass=Singleton):
    """Provide access to the application configuration (singleton)"""

    def __init__(self):
        super().__init__(USER_APP_CONFIG, DEFAULT_APP_CONFIG)
