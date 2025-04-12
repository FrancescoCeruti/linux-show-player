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
from PyQt5.QtWidgets import (
    QGroupBox,
    QComboBox,
    QVBoxLayout,
)

from lisp.plugins.gst_backend.elements.flip import Flip
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class FlipSettings(SettingsPage):
    ELEMENT = Flip
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.methodGroup = QGroupBox(self)
        self.methodGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.methodGroup)

        self.methodComboBox = QComboBox(self.methodGroup)
        self.methodComboBox.addItem(translate("FlipSettings", "None"), 0)
        self.methodComboBox.addItem(translate("FlipSettings", "Clockwise 90°"), 1)
        self.methodComboBox.addItem(translate("FlipSettings", "Rotate 180°"), 2)
        self.methodComboBox.addItem(translate("FlipSettings", "Counterclockwise 90°"), 3)
        self.methodComboBox.addItem(translate("FlipSettings", "Horizontal Flip"), 4)
        self.methodComboBox.addItem(translate("FlipSettings", "Vertial Flip"), 5)
        self.methodComboBox.addItem(translate("FlipSettings", "Diagonal Flip (upper-left / lower-right)"), 6)
        self.methodComboBox.addItem(translate("FlipSettings", "Diagonal Flip (upper-right / lower-left)"), 7)
        self.methodGroup.layout().addWidget(self.methodComboBox)

        self.retranslateUi()

    def retranslateUi(self):
        self.methodGroup.setTitle(translate("FlipSettings", "Method"))

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.methodGroup, enabled)

    def getSettings(self):
        settings = {}

        if self.isGroupEnabled(self.methodGroup):
            settings["method"] = self.methodComboBox.currentData()

        return settings

    def loadSettings(self, settings):
        self.methodComboBox.setCurrentIndex(settings.get("method", 1))
