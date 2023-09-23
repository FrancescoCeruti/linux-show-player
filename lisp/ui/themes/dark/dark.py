# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

import os

from PyQt5.QtGui import QColor, QPalette

# Import resources
# pylint: disable=unused-import
# noinspection PyUnresolvedReferences
from . import assets


class Dark:
    QssPath = os.path.join(os.path.dirname(__file__), "theme.qss")

    def apply(self, qt_app):
        background = QColor(30, 30, 30)
        foreground = QColor(52, 52, 52)
        text = QColor(230, 230, 230)
        highlight = QColor(65, 155, 230)

        palette = qt_app.palette()
        palette.setColor(QPalette.Window, foreground)
        palette.setColor(QPalette.WindowText, text)
        palette.setColor(QPalette.Base, background)
        palette.setColor(QPalette.AlternateBase, foreground.darker(125))
        palette.setColor(QPalette.ToolTipBase, foreground)
        palette.setColor(QPalette.ToolTipText, text)
        palette.setColor(QPalette.Text, text)
        palette.setColor(QPalette.Button, foreground)
        palette.setColor(QPalette.ButtonText, text)
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, highlight)

        palette.setColor(QPalette.Light, foreground.lighter(160))
        palette.setColor(QPalette.Midlight, foreground.lighter(125))
        palette.setColor(QPalette.Dark, foreground.darker(150))
        palette.setColor(QPalette.Mid, foreground.darker(125))

        palette.setColor(QPalette.Highlight, highlight)
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))

        qt_app.setPalette(palette)

        with open(Dark.QssPath, mode="r", encoding="utf-8") as f:
            qt_app.setStyleSheet(f.read())
