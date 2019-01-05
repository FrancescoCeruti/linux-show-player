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
# noinspection PyUnresolvedReferences
from . import assetes


class Dark:
    QssPath = os.path.join(os.path.dirname(__file__), "theme.qss")

    def apply(self, qt_app):
        with open(Dark.QssPath, mode="r", encoding="utf-8") as f:
            qt_app.setStyleSheet(f.read())

        # Change link color
        palette = qt_app.palette()
        palette.setColor(QPalette.Link, QColor(65, 155, 230))
        palette.setColor(QPalette.LinkVisited, QColor(43, 103, 153))
        qt_app.setPalette(palette)
