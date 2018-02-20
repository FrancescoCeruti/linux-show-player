# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from lisp import ICON_THEMES_DIR


class Theme:
    Name = 'Theme'

    def apply(self, qt_app):
        """
        :type qt_app: PyQt5.QtWidgets.QApplication
        """


class IconTheme:
    BLANK = QIcon()

    _GlobalCache = {}
    _GlobalTheme = None

    def __init__(self, *dirs):
        self._lookup_dirs = [
            os.path.join(ICON_THEMES_DIR, d) for d in dirs
        ]

    def __iter__(self):
        yield from self._lookup_dirs

    @staticmethod
    def get(icon_name):
        icon = IconTheme._GlobalCache.get(icon_name, None)

        if icon is None:
            icon = IconTheme.BLANK
            for dir_ in IconTheme.theme():
                for icon in glob.iglob(os.path.join(dir_, icon_name) + '.*'):
                    icon = QIcon(icon)

            IconTheme._GlobalCache[icon_name] = icon

        return icon

    @staticmethod
    def theme():
        return IconTheme._GlobalTheme

    @staticmethod
    def set_theme(theme):
        IconTheme.clean_cache()
        IconTheme._GlobalTheme = theme

    @staticmethod
    def clean_cache():
        IconTheme._GlobalCache.clear()
