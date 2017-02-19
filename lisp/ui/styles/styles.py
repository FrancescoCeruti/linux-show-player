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

import sys
import os.path
from collections import namedtuple

from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QStyleFactory, qApp

try:
    from os import scandir
except ImportError:
    from scandir import scandir

StylesPath = os.path.abspath(os.path.dirname(__file__))
IconsThemePaths = [os.path.join(StylesPath, 'icons')]

LiSPStyles = {}
Style = namedtuple('Style', ['path', 'has_qss', 'has_py'])


def styles():
    """Returns all available styles (Qt and installed)."""
    return QStyleFactory.keys() + list(LiSPStyles.keys())


def scan_styles():
    """Scan for "installed" styles."""
    LiSPStyles.clear()

    for entry in scandir(StylesPath):
        if entry.is_dir():
            has_qss = os.path.exists(os.path.join(entry.path, 'style.qss'))
            has_py = os.path.exists(os.path.join(entry.path, 'style.py'))

            if has_qss or has_py:
                LiSPStyles[entry.name.title()] = Style(
                    path=entry.path,
                    has_qss=has_qss,
                    has_py=has_py
                )


def __load_qss_style(path):
    """Read and load the stylesheet file."""
    with open(path, mode='r', encoding='utf-8') as f:
        style = f.read()

    qApp.setStyleSheet(style)


def __load_py_style(module):
    """Load the python style module."""
    __import__(module, globals(), locals(), ['*'])


def apply_style(name):
    """Load a style given its name."""
    style = LiSPStyles.get(name.title())

    if isinstance(style, Style):
        if style.has_py:
            module = __package__ + '.' + os.path.basename(style.path) + '.style'
            __load_py_style(module)

        if style.has_qss:
            __load_qss_style(os.path.join(style.path, 'style.qss'))
    else:
        qApp.setStyleSheet('')
        qApp.setStyle(QStyleFactory.create(name))


# Search for styles
scan_styles()
