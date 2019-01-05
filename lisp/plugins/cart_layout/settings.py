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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QCheckBox,
    QGridLayout,
    QSpinBox,
    QLabel,
)

from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class CartLayoutSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Cart Layout")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.behaviorsGroup = QGroupBox(self)
        self.behaviorsGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.behaviorsGroup)

        self.countdownMode = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.countdownMode)

        self.showSeek = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showSeek)

        self.showDbMeters = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showDbMeters)

        self.showAccurate = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showAccurate)

        self.showVolume = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showVolume)

        self.gridSizeGroup = QGroupBox(self)
        self.gridSizeGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.gridSizeGroup)

        self.columnsLabel = QLabel(self.gridSizeGroup)
        self.gridSizeGroup.layout().addWidget(self.columnsLabel, 0, 0)
        self.columnsSpin = QSpinBox(self.gridSizeGroup)
        self.columnsSpin.setRange(1, 16)
        self.gridSizeGroup.layout().addWidget(self.columnsSpin, 0, 1)

        self.rowsLabel = QLabel(self.gridSizeGroup)
        self.gridSizeGroup.layout().addWidget(self.rowsLabel, 1, 0)
        self.rowsSpin = QSpinBox(self.gridSizeGroup)
        self.rowsSpin.setRange(1, 16)
        self.gridSizeGroup.layout().addWidget(self.rowsSpin, 1, 1)

        self.gridSizeGroup.layout().setColumnStretch(0, 1)
        self.gridSizeGroup.layout().setColumnStretch(1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.behaviorsGroup.setTitle(
            translate("CartLayout", "Default behaviors")
        )
        self.countdownMode.setText(translate("CartLayout", "Countdown mode"))
        self.showSeek.setText(translate("CartLayout", "Show seek-bars"))
        self.showDbMeters.setText(translate("CartLayout", "Show dB-meters"))
        self.showAccurate.setText(translate("CartLayout", "Show accurate time"))
        self.showVolume.setText(translate("CartLayout", "Show volume"))
        self.gridSizeGroup.setTitle(translate("CartLayout", "Grid size"))
        self.columnsLabel.setText(translate("CartLayout", "Number of columns:"))
        self.rowsLabel.setText(translate("CartLayout", "Number of rows:"))

    def loadSettings(self, settings):
        self.columnsSpin.setValue(settings["grid"]["columns"])
        self.rowsSpin.setValue(settings["grid"]["rows"])
        self.showSeek.setChecked(settings["show"]["seekSliders"])
        self.showDbMeters.setChecked(settings["show"]["dBMeters"])
        self.showAccurate.setChecked(settings["show"]["accurateTime"])
        self.showVolume.setChecked(settings["show"]["volumeControls"])
        self.countdownMode.setChecked(settings["countdownMode"])

    def getSettings(self):
        return {
            "grid": {
                "columns": self.columnsSpin.value(),
                "rows": self.rowsSpin.value(),
            },
            "show": {
                "dBMeters": self.showDbMeters.isChecked(),
                "seekSliders": self.showSeek.isChecked(),
                "accurateTime": self.showAccurate.isChecked(),
                "volumeControls": self.showVolume.isChecked(),
            },
            "countdownMode": self.countdownMode.isChecked(),
        }
