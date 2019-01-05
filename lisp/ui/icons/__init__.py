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

import glob
import os

from PyQt5.QtGui import QIcon

from lisp import ICON_THEMES_DIR, ICON_THEME_COMMON


def icon_themes_names():
    for entry in os.scandir(os.path.dirname(__file__)):
        if (
            entry.is_dir()
            and entry.name != ICON_THEME_COMMON
            and entry.name[0] != "_"
        ):
            yield entry.name


class IconTheme:
    _SEARCH_PATTERN = "{}/**/{}.*"
    _BLANK_ICON = QIcon()
    _GlobalCache = {}
    _GlobalTheme = None

    def __init__(self, *names):
        self._lookup_dirs = [os.path.join(ICON_THEMES_DIR, d) for d in names]

    def __iter__(self):
        yield from self._lookup_dirs

    @staticmethod
    def get(icon_name):
        icon = IconTheme._GlobalCache.get(icon_name, None)

        if icon is None:
            icon = IconTheme._BLANK_ICON
            for dir_ in IconTheme._GlobalTheme:
                pattern = IconTheme._SEARCH_PATTERN.format(dir_, icon_name)
                for icon in glob.iglob(pattern, recursive=True):
                    icon = QIcon(icon)
                    break

            IconTheme._GlobalCache[icon_name] = icon

        return icon

    @staticmethod
    def set_theme_name(theme_name):
        IconTheme._GlobalCache.clear()
        IconTheme._GlobalTheme = IconTheme(theme_name, ICON_THEME_COMMON)
