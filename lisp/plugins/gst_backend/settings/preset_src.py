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

from PyQt5.QtCore import Qt, QTime
from PyQt5.QtWidgets import QGroupBox, QComboBox, QVBoxLayout, QTimeEdit

from lisp.plugins.gst_backend.elements.preset_src import PresetSrc
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class PresetSrcSettings(SettingsPage):
    ELEMENT = PresetSrc
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.functionGroup = QGroupBox(self)
        self.functionGroup.setTitle(translate("PresetSrcSettings", "Presets"))
        self.functionGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.functionGroup)

        self.functionCombo = QComboBox(self.functionGroup)
        self.functionGroup.layout().addWidget(self.functionCombo)

        for function in sorted(PresetSrc.PRESETS.keys()):
            self.functionCombo.addItem(function)

        self.functionDuration = QTimeEdit(self.functionGroup)
        self.functionDuration.setDisplayFormat("HH.mm.ss.zzz")
        self.functionGroup.layout().addWidget(self.functionDuration)

    def enableCheck(self, enabled):
        self.functionGroup.setCheckable(enabled)
        self.functionGroup.setChecked(False)

    def getSettings(self):
        if not (
            self.functionGroup.isCheckable()
            and not self.functionGroup.isChecked()
        ):
            return {
                "preset": self.functionCombo.currentText(),
                "duration": self.functionDuration.time().msecsSinceStartOfDay(),
            }

        return {}

    def loadSettings(self, settings):
        self.functionCombo.setCurrentText(settings.get("preset", ""))
        self.functionDuration.setTime(
            QTime.fromMSecsSinceStartOfDay(settings.get("duration", 0))
        )
