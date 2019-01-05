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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QSizePolicy

from lisp.plugins.list_layout.list_view import CueListView
from lisp.plugins.list_layout.playing_view import RunningCuesListWidget
from .control_buttons import ShowControlButtons
from .info_panel import InfoPanel


class ListLayoutView(QWidget):
    def __init__(self, listModel, runModel, config, *args):
        super().__init__(*args)
        self.setLayout(QGridLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.listModel = listModel

        # GO-BUTTON (top-left)
        self.goButton = QPushButton("GO", self)
        self.goButton.setFocusPolicy(Qt.NoFocus)
        self.goButton.setFixedWidth(120)
        self.goButton.setFixedHeight(100)
        self.goButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.goButton.setStyleSheet("font-size: 48pt;")
        self.layout().addWidget(self.goButton, 0, 0)

        # INFO PANEL (top-center)
        self.infoPanel = InfoPanel(self)
        self.infoPanel.setFixedHeight(120)
        self.layout().addWidget(self.infoPanel, 0, 1)

        # CONTROL-BUTTONS (top-right)
        self.controlButtons = ShowControlButtons(self)
        self.controlButtons.setFixedHeight(120)
        self.layout().addWidget(self.controlButtons, 0, 2)

        # CUE VIEW (center-left)
        self.listView = CueListView(listModel, self)
        self.listView.currentItemChanged.connect(self.__listViewCurrentChanged)
        self.layout().addWidget(self.listView, 1, 0, 1, 2)

        # PLAYING VIEW (center-right)
        self.runView = RunningCuesListWidget(runModel, config, parent=self)
        self.runView.setMinimumWidth(300)
        self.runView.setMaximumWidth(300)
        self.layout().addWidget(self.runView, 1, 2)

    def __listViewCurrentChanged(self, current, _):
        cue = None
        if current is not None:
            index = self.listView.indexOfTopLevelItem(current)
            cue = self.listModel.item(index)

        self.infoPanel.cue = cue
