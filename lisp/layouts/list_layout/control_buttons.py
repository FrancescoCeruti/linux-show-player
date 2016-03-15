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

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QSizePolicy


class ControlButtons(QWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QGridLayout())
        self.layout().setContentsMargins(0, 10, 0, 10)
        self.layout().setSpacing(10)

        hPolicy = QSizePolicy.Ignored
        vPolicy = QSizePolicy.Expanding
        iconSize = QSize(48, 48)

        self.stopButton = QPushButton(self)
        self.stopButton.setToolTip('Stop all')
        self.stopButton.setFocusPolicy(Qt.NoFocus)
        self.stopButton.setSizePolicy(hPolicy, vPolicy)
        self.stopButton.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.stopButton.setIconSize(iconSize)
        self.layout().addWidget(self.stopButton, 0, 0)

        self.pauseButton = QPushButton(self)
        self.pauseButton.setToolTip('Pause all')
        self.pauseButton.setFocusPolicy(Qt.NoFocus)
        self.pauseButton.setSizePolicy(hPolicy, vPolicy)
        self.pauseButton.setIcon(QIcon.fromTheme("media-playback-pause"))
        self.pauseButton.setIconSize(iconSize)
        self.layout().addWidget(self.pauseButton, 0, 1)

        self.restartButton = QPushButton(self)
        self.restartButton.setToolTip('Restart all')
        self.restartButton.setFocusPolicy(Qt.NoFocus)
        self.restartButton.setSizePolicy(hPolicy, vPolicy)
        self.restartButton.setIcon(QIcon.fromTheme("media-playback-start"))
        self.restartButton.setIconSize(iconSize)
        self.layout().addWidget(self.restartButton, 0, 2)
