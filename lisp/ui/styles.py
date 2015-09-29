# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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

from os import path

from PyQt5.QtCore import QFileSystemWatcher
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QStyleFactory, qApp

from lisp.ui.style import style  # @UnusedImport

# TODO: maybe a class ? (StyleManager)

__ThemeFileWatcher = None

StylePath = path.abspath(path.join(path.dirname(__file__)))
IconsThemePaths = [path.join(StylePath, 'icons')]
IconsThemeName = 'lisp'

LiSPThemeFile = path.join(StylePath, 'style/style.qss')


def __load_qss_theme(qss_file, update=False):
    with open(qss_file, mode='r', encoding='utf-8') as f:
        style = f.read()

    qApp.setStyleSheet(style)

    if not update:
        watched_files = __ThemeFileWatcher.files()
        if len(watched_files) > 0:
            __ThemeFileWatcher.removePaths(watched_files)

        __ThemeFileWatcher.addPath(qss_file)


def __update_style():
    watched_files = __ThemeFileWatcher.files()

    if len(watched_files) > 0:
        __load_qss_theme(watched_files[0], update=True)


def apply_style(style_name):
    global __ThemeFileWatcher
    if __ThemeFileWatcher is None:
        __ThemeFileWatcher = QFileSystemWatcher()
        __ThemeFileWatcher.fileChanged.connect(__update_style)

    if style_name == 'LiSP':
        __load_qss_theme(LiSPThemeFile)

        # Change link color
        palette = qApp.palette()
        palette.setColor(QPalette.Link, QColor(65, 155, 230))
        palette.setColor(QPalette.LinkVisited, QColor(43, 103, 153))
        qApp.setPalette(palette)
    else:
        qApp.setStyleSheet('')
        qApp.setStyle(QStyleFactory.create(style_name))


def get_styles():
    return QStyleFactory.keys() + ['LiSP']