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
from xml.etree import ElementTree as ET

from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import Qt, QByteArray

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
    _GLOB_PATTERN = "{}/**/{}.*"
    _BLANK_ICON = QIcon()
    _VARIANTS = {
        "-cart": {"stroke": "black", "fill": "black", "opacity": "0.1"},
        "-running": {"stroke": "#0D0", "fill": "#0D0", "opacity": "1"},
        "-pause": {"stroke": "#F90", "fill": "#F90", "opacity": "1"},
        "-error": {"stroke": "#D11", "fill": "#D11", "opacity": "1"},
    }
    _GlobalCache = {}
    _GlobalTheme = None

    def __init__(self, *names):
        self._lookup_dirs = [os.path.join(ICON_THEMES_DIR, d) for d in names]

    def __iter__(self):
        yield from self._lookup_dirs

    @staticmethod
    def get(icon_name: str) -> QIcon:
        icon = IconTheme._GlobalCache.get(icon_name, None)

        if icon is not None:
            return icon

        for search_dir in IconTheme._GlobalTheme:
            icon = IconTheme._get_icon(search_dir, icon_name)
            if icon is not None:
                break

        if icon is None:
            icon = IconTheme._BLANK_ICON

        IconTheme._GlobalCache[icon_name] = icon

        return icon

    @staticmethod
    def _get_icon(search_dir: str, icon_name: str) -> QIcon | None:
        pattern = IconTheme._GLOB_PATTERN.format(search_dir, icon_name)
        for icon in glob.iglob(pattern, recursive=True):
            return QIcon(icon)

        icon_name, suffix = IconTheme._split_variant(icon_name)
        if suffix:
            pattern = IconTheme._GLOB_PATTERN.format(search_dir, icon_name)
            for icon in glob.iglob(pattern, recursive=True):
                return IconTheme._load_modified_icon(icon, suffix)

    @staticmethod
    def set_theme_name(theme_name: str):
        IconTheme._GlobalCache.clear()
        IconTheme._GlobalTheme = IconTheme(theme_name, ICON_THEME_COMMON)

        QIcon.setThemeSearchPaths([ICON_THEMES_DIR])
        QIcon.setThemeName(theme_name)

    @staticmethod
    def _split_variant(icon_name: str) -> tuple[str, str]:
        for suffix in IconTheme._VARIANTS:
            if icon_name.endswith(suffix):
                return (icon_name[: -len(suffix)], suffix)

        return (icon_name, "")

    @staticmethod
    def _load_modified_icon(icon_path: str, suffix: str) -> QIcon | None:
        try:
            with open(icon_path, "rb") as icon_file:
                icon_content = icon_file.read()

            root = ET.fromstring(icon_content)
            variant = IconTheme._VARIANTS[suffix]
            for attr, val in variant.items():
                root.set(attr, val)

            renderer = QSvgRenderer(
                QByteArray(
                    ET.tostring(root, encoding="utf-8", xml_declaration=True)
                )
            )

            pixmap = QPixmap(renderer.defaultSize())
            pixmap.fill(Qt.transparent)

            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            return QIcon(pixmap)
        except Exception:
            return None
