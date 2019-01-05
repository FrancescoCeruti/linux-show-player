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

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGroupBox,
    QGridLayout,
    QSpinBox,
    QLabel,
    QVBoxLayout,
)

from lisp.plugins.gst_backend.elements.db_meter import DbMeter
from lisp.plugins.gst_backend.gi_repository import Gst
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class DbMeterSettings(SettingsPage):

    ELEMENT = DbMeter
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.groupBox = QGroupBox(self)
        self.groupBox.setGeometry(0, 0, self.width(), 180)
        self.groupBox.setLayout(QGridLayout())
        self.layout().addWidget(self.groupBox)

        # Time (sec/100) between two levels
        self.intervalSpin = QSpinBox(self.groupBox)
        self.intervalSpin.setRange(1, 1000)
        self.intervalSpin.setMaximum(1000)
        self.intervalSpin.setValue(50)
        self.groupBox.layout().addWidget(self.intervalSpin, 0, 0)

        self.intervalLabel = QLabel(self.groupBox)
        self.intervalLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.layout().addWidget(self.intervalLabel, 0, 1)

        # Peak ttl (sec/100)
        self.ttlSpin = QSpinBox(self.groupBox)
        self.ttlSpin.setSingleStep(10)
        self.ttlSpin.setRange(10, 10000)
        self.ttlSpin.setValue(500)
        self.groupBox.layout().addWidget(self.ttlSpin, 1, 0)

        self.ttlLabel = QLabel(self.groupBox)
        self.ttlLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.layout().addWidget(self.ttlLabel, 1, 1)

        # Peak falloff (unit per time)
        self.falloffSpin = QSpinBox(self.groupBox)
        self.falloffSpin.setRange(1, 100)
        self.falloffSpin.setValue(20)
        self.groupBox.layout().addWidget(self.falloffSpin, 2, 0)

        self.falloffLabel = QLabel(self.groupBox)
        self.falloffLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.layout().addWidget(self.falloffLabel, 2, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.groupBox.setTitle(translate("DbMeterSettings", "DbMeter settings"))
        self.intervalLabel.setText(
            translate("DbMeterSettings", "Time between levels (ms)")
        )
        self.ttlLabel.setText(translate("DbMeterSettings", "Peak ttl (ms)"))
        self.falloffLabel.setText(
            translate("DbMeterSettings", "Peak falloff (dB/sec)")
        )

    def loadSettings(self, settings):
        self.intervalSpin.setValue(settings.get("interval", 50) / Gst.MSECOND)
        self.ttlSpin.setValue(settings.get("peak_ttl", 500) / Gst.MSECOND)
        self.falloffSpin.setValue(settings.get("peak_falloff", 20))

    def getSettings(self):
        settings = {}

        if not (self.groupBox.isCheckable() and not self.groupBox.isChecked()):
            settings["interval"] = self.intervalSpin.value() * Gst.MSECOND
            settings["peak_ttl"] = self.ttlSpin.value() * Gst.MSECOND
            settings["peak_falloff"] = self.falloffSpin.value()

        return settings
