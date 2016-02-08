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

import math

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QGridLayout, QComboBox, QDoubleSpinBox, \
    QLabel, QVBoxLayout

from lisp.backends.gst.elements.audiodynamic import Audiodynamic
from lisp.backends.gst.settings.settings_page import GstElementSettingsPage


MIN_dB = 0.000000312  # -100dB


class AudiodynamicSettings(GstElementSettingsPage):

    NAME = "Compressor/Expander"
    ELEMENT = Audiodynamic

    def __init__(self, element_id, **kwargs):
        super().__init__(element_id)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.groupBox = QGroupBox(self)
        self.groupBox.setGeometry(0, 0, self.width(), 240)
        self.groupBox.setLayout(QGridLayout())
        self.layout().addWidget(self.groupBox)

        self.comboMode = QComboBox(self.groupBox)
        self.comboMode.addItem("Compressor")
        self.comboMode.addItem("Expander")
        self.groupBox.layout().addWidget(self.comboMode, 0, 0, 1, 1)

        self.comboCh = QComboBox(self.groupBox)
        self.comboCh.addItem("Soft Knee")
        self.comboCh.addItem("Hard Knee")
        self.groupBox.layout().addWidget(self.comboCh, 1, 0, 1, 1)

        self.spinRatio = QDoubleSpinBox(self.groupBox)
        self.groupBox.layout().addWidget(self.spinRatio, 2, 0, 1, 1)

        self.spinThreshold = QDoubleSpinBox(self.groupBox)
        self.spinThreshold.setMaximum(0)
        self.spinThreshold.setMinimum(-100)
        self.spinThreshold.setSingleStep(1)
        self.groupBox.layout().addWidget(self.spinThreshold, 3, 0, 1, 1)

        self.labelMode = QLabel(self.groupBox)
        self.labelMode.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.layout().addWidget(self.labelMode, 0, 1, 1, 1)

        self.labelCh = QLabel(self.groupBox)
        self.labelCh.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.layout().addWidget(self.labelCh, 1, 1, 1, 1)

        self.labelRatio = QLabel(self.groupBox)
        self.labelRatio.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.layout().addWidget(self.labelRatio, 2, 1, 1, 1)

        self.labelThreshold = QLabel(self.groupBox)
        self.labelThreshold.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.layout().addWidget(self.labelThreshold, 3, 1, 1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.groupBox.setTitle("Audio Dynamic - Compressor/Expander")
        self.labelMode.setText("Type")
        self.labelCh.setText("Curve Shape")
        self.labelRatio.setText("Ratio")
        self.labelThreshold.setText("Threshold (dB)")

    def enable_check(self, enable):
        self.groupBox.setCheckable(enable)
        self.groupBox.setChecked(False)

    def get_settings(self):
        conf = {}

        if(not (self.groupBox.isCheckable() and
                not self.groupBox.isChecked())):
            conf = {"ratio": self.spinRatio.value(),
                    "threshold": math.pow(10, self.spinThreshold.value() / 20)}

            if(self.comboMode.currentIndex() == 0):
                conf["mode"] = "compressor"
            else:
                conf["mode"] = "expander"

            if(self.comboCh.currentIndex() == 0):
                conf["characteristics"] = "soft-knee"
            else:
                conf["characteristics"] = "hard-knee"

            conf = {self.id: conf}

        return conf

    def load_settings(self, settings):
        if(settings is not None):
            if(self.id in settings):
                if(settings[self.id]["mode"] == "compressor"):
                    self.comboMode.setCurrentIndex(0)
                else:
                    self.comboMode.setCurrentIndex(1)

                if(settings[self.id]["characteristics"] == "soft-knee"):
                    self.comboCh.setCurrentIndex(0)
                else:
                    self.comboCh.setCurrentIndex(1)

                if (settings[self.id]["threshold"] == 0):
                    settings[self.id]["threshold"] = MIN_dB

                self.spinThreshold.setValue(
                    20 * math.log10(settings[self.id]["threshold"]))
                self.spinRatio.setValue(settings[self.id]["ratio"])
