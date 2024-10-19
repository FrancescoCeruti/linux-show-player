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

import json
import logging
from abc import ABCMeta, abstractmethod
from os import path
from shutil import copyfile

from lisp.core.collections.nested_dict import _UNSET, NestedDict
from lisp.core.signal import Signal
from lisp.core.util import dict_merge_diff
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class Configuration(NestedDict, metaclass=ABCMeta):
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

    def get(self, key: str, default=_UNSET):
        value = super().get(key, default)

        if value is default:
            logger.info(
                translate(
                    "ConfigurationInfo",
                    'Invalid path "{}", return default.',
                ).format(key)
            )

        return value

    def set(self, key: str, value):
        changed = super().set(key, value)
        if changed:
            self.changed.emit(key, value)

        return changed

    def update(self, other: dict = None, **kwargs):
        diff = dict_merge_diff(self._root, other)
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

        logger.debug(
            translate(
                "ConfigurationDebug", "Configuration read from {}"
            ).format(self.user_path)
        )

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
    def _read_json(key):
        with open(key, "r") as f:
            return json.load(f)
