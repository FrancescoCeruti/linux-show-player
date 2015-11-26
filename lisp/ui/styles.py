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

from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QStyleFactory, qApp, QProxyStyle, QStyle

# NEEDED to load assets
from lisp.ui.style import style

# TODO: maybe a class ? (StyleManager)

StylePath = path.abspath(path.join(path.dirname(__file__)))
IconsThemePaths = [path.join(StylePath, 'icons')]

LiSPThemeFile = path.join(StylePath, 'style/style.qss')


class NoFocusRectProxyStyle(QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget):
        # do not draw focus rectangles - this permits modern styling
        if element != QStyle.PE_FrameFocusRect:
            super().drawPrimitive(element, option, painter, widget)


def __load_qss_theme(qss_file):
    with open(qss_file, mode='r', encoding='utf-8') as f:
        style = f.read()

    qApp.setStyleSheet(style)


def apply_style(style_name):
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
