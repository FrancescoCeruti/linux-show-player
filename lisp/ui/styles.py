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
from PyQt5.QtWidgets import QStyleFactory, qApp

from lisp.ui.style import style  # @UnusedImport


StylePath = path.abspath(path.join(path.dirname(__file__))) + '/'
IconsThemePaths = [StylePath + 'icons']
IconsThemeName = 'lisp'

QLiSPTheme = ''
with open(StylePath + 'style/style.qss', mode='r', encoding='utf-8') as f:
    QLiSPTheme = f.read()


def get_styles():
    return QStyleFactory.keys() + ['LiSP']


def apply_style(style_name):
    if style_name == 'LiSP':
        qApp.setStyleSheet(QLiSPTheme)

        # Change link color
        palette = qApp.palette()
        palette.setColor(QPalette.Link, QColor(65, 155, 230))
        palette.setColor(QPalette.LinkVisited, QColor(43, 103, 153))
        qApp.setPalette(palette)
    else:
        qApp.setStyleSheet('')
        qApp.setStyle(QStyleFactory.create(style_name))
