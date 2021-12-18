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
from PyQt5.QtWidgets import QWidget, QSizePolicy, QSplitter, QVBoxLayout

from lisp.plugins.list_layout.list_view import CueListView
from lisp.plugins.list_layout.playing_view import RunningCuesListWidget
from lisp.ui.widgets.dynamicfontsize import DynamicFontSizePushButton
from .control_buttons import ShowControlButtons
from .info_panel import InfoPanel


class ListLayoutView(QWidget):
    def __init__(self, listModel, runModel, config, *args):
        super().__init__(*args)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.listModel = listModel

        self.mainSplitter = QSplitter(Qt.Vertical, self)
        self.layout().addWidget(self.mainSplitter)

        self.topSplitter = QSplitter(self.mainSplitter)
        self.mainSplitter.addWidget(self.topSplitter)

        self.centralSplitter = QSplitter(self.topSplitter)
        self.mainSplitter.addWidget(self.centralSplitter)

        # GO-BUTTON (top-left)
        self.goButton = DynamicFontSizePushButton(parent=self)
        self.goButton.setText("GO")
        self.goButton.setMinimumWidth(60)
        self.goButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.goButton.setFocusPolicy(Qt.NoFocus)
        self.topSplitter.addWidget(self.goButton)

        # INFO PANEL (top-center)
        self.infoPanel = InfoPanel(self)
        self.infoPanel.setMinimumWidth(300)
        self.infoPanel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Ignored)
        self.infoPanel.cueDescription.setFontPointSize(
            config.get(
                "infoPanelFontSize",
                self.infoPanel.cueDescription.fontPointSize(),
            )
        )
        self.topSplitter.addWidget(self.infoPanel)

        # CONTROL-BUTTONS (top-right)
        self.controlButtons = ShowControlButtons(self)
        self.controlButtons.setMinimumWidth(100)
        self.controlButtons.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Minimum
        )
        self.topSplitter.addWidget(self.controlButtons)

        # CUE VIEW (center-left)
        self.listView = CueListView(listModel, self)
        self.listView.setMinimumWidth(200)
        self.listView.currentItemChanged.connect(self.__listViewCurrentChanged)
        self.centralSplitter.addWidget(self.listView)
        self.centralSplitter.setCollapsible(0, False)

        # PLAYING VIEW (center-right)
        self.runView = RunningCuesListWidget(runModel, config, parent=self)
        self.runView.setMinimumWidth(200)
        self.runView.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.centralSplitter.addWidget(self.runView)

        self.__userResized = False

    def showEvent(self, event):
        super().showEvent(event)
        if not self.__userResized:
            self.resetSize()

    def resetSize(self):
        self.mainSplitter.setSizes(
            (int(0.22 * self.width()), int(0.78 * self.width()))
        )
        self.centralSplitter.setSizes(
            (int(0.78 * self.width()), int(0.22 * self.width()))
        )
        self.topSplitter.setSizes(
            (
                int(0.11 * self.width()),
                int(0.67 * self.width()),
                int(0.22 * self.width()),
            )
        )

    def getSplitterSizes(self):
        return [
            self.mainSplitter.sizes(),
            self.topSplitter.sizes(),
            self.centralSplitter.sizes(),
        ]

    def setSplitterSize(self, sizes):
        if len(sizes) >= 3:
            self.mainSplitter.setSizes(sizes[0])
            self.topSplitter.setSizes(sizes[1])
            self.centralSplitter.setSizes(sizes[2])

            self.__userResized = True

    def setResizeHandlesEnabled(self, enabled):
        self.__setSplitterHandlesEnabled(self.mainSplitter, enabled)
        self.__setSplitterHandlesEnabled(self.topSplitter, enabled)
        self.__setSplitterHandlesEnabled(self.centralSplitter, enabled)

    def __setSplitterHandlesEnabled(self, splitter: QSplitter, enabled):
        for n in range(splitter.count()):
            splitter.handle(n).setEnabled(enabled)

    def __listViewCurrentChanged(self, current, _):
        cue = None
        if current is not None:
            index = self.listView.indexOfTopLevelItem(current)
            if index < len(self.listModel):
                cue = self.listModel.item(index)

        self.infoPanel.cue = cue
