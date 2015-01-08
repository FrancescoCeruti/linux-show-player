##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import math

from PyQt5.QtWidgets import *  # @UnusedWildImport
from PyQt5 import QtCore

from lisp.gst.elements.audiodynamic import Audiodynamic
from lisp.ui.settings.section import SettingsSection


MIN_dB = 0.000000312  # -100dB


class AudiodynamicSettings(SettingsSection):

    NAME = "Compressor/Expander"
    ELEMENT = Audiodynamic

    def __init__(self, size, Id, parent=None):
        super().__init__(size, parent)

        self.id = Id

        self.groupBox = QGroupBox(self)
        self.groupBox.setGeometry(0, 0, self.width(), 240)

        self.gridLayout = QGridLayout(self.groupBox)

        self.comboMode = QComboBox(self.groupBox)
        self.comboMode.addItem("Compressor")
        self.comboMode.addItem("Expander")
        self.gridLayout.addWidget(self.comboMode, 0, 0, 1, 1)

        self.comboCh = QComboBox(self.groupBox)
        self.comboCh.addItem("Soft Knee")
        self.comboCh.addItem("Hard Knee")
        self.gridLayout.addWidget(self.comboCh, 1, 0, 1, 1)

        self.spinRatio = QDoubleSpinBox(self.groupBox)
        self.gridLayout.addWidget(self.spinRatio, 2, 0, 1, 1)

        self.spinThreshold = QDoubleSpinBox(self.groupBox)
        self.spinThreshold.setMaximum(0)
        self.spinThreshold.setMinimum(-100)
        self.spinThreshold.setSingleStep(1)
        self.gridLayout.addWidget(self.spinThreshold, 3, 0, 1, 1)

        self.labelMode = QLabel(self.groupBox)
        self.labelMode.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.labelMode, 0, 1, 1, 1)

        self.labelCh = QLabel(self.groupBox)
        self.labelCh.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.labelCh, 1, 1, 1, 1)

        self.labelRatio = QLabel(self.groupBox)
        self.labelRatio.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.labelRatio, 2, 1, 1, 1)

        self.labelThreshold = QLabel(self.groupBox)
        self.labelThreshold.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.labelThreshold, 3, 1, 1, 1)

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

    def get_configuration(self):
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

    def set_configuration(self, conf):
        if(conf is not None):
            if(self.id in conf):
                if(conf[self.id]["mode"] == "compressor"):
                    self.comboMode.setCurrentIndex(0)
                else:
                    self.comboMode.setCurrentIndex(1)

                if(conf[self.id]["characteristics"] == "soft-knee"):
                    self.comboCh.setCurrentIndex(0)
                else:
                    self.comboCh.setCurrentIndex(1)

                if (conf[self.id]["threshold"] == 0):
                    conf[self.id]["threshold"] = MIN_dB

                self.spinThreshold.setValue(
                    20 * math.log10(conf[self.id]["threshold"]))
                self.spinRatio.setValue(conf[self.id]["ratio"])
