##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5 import QtCore
from PyQt5.QtWidgets import QGroupBox, QGridLayout, QSpinBox, QLabel

from lisp.gst.elements.dbmeter import Dbmeter
from lisp.ui.settings.section import SettingsSection


class DbmeterSettings(SettingsSection):

    NAME = 'DbMeter'
    ELEMENT = Dbmeter

    def __init__(self, size, Id, parent=None):
        super().__init__(size, parent)

        self.id = Id

        self.groupBox = QGroupBox(self)
        self.groupBox.setGeometry(0, 0, self.width(), 180)

        self.layout = QGridLayout(self.groupBox)

        # Time (sec/100) between two levels
        self.intervalSpin = QSpinBox(self.groupBox)
        self.intervalSpin.setRange(1, 1000)
        self.intervalSpin.setMaximum(1000)
        self.intervalSpin.setValue(50)
        self.layout.addWidget(self.intervalSpin, 0, 0)

        self.intervalLabel = QLabel(self.groupBox)
        self.intervalLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.intervalLabel, 0, 1)

        # Peak ttl (sec/100)
        self.ttlSpin = QSpinBox(self.groupBox)
        self.ttlSpin.setSingleStep(10)
        self.ttlSpin.setRange(10, 10000)
        self.ttlSpin.setValue(500)
        self.layout.addWidget(self.ttlSpin, 1, 0)

        self.ttlLabel = QLabel(self.groupBox)
        self.ttlLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.ttlLabel, 1, 1)

        # Peak falloff (unit per time)
        self.falloffSpin = QSpinBox(self.groupBox)
        self.falloffSpin.setRange(1, 100)
        self.falloffSpin.setValue(20)
        self.layout.addWidget(self.falloffSpin, 2, 0)

        self.falloffLabel = QLabel(self.groupBox)
        self.falloffLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.falloffLabel, 2, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.groupBox.setTitle("VUMeter settings")
        self.intervalLabel.setText("Time between levels (ms)")
        self.ttlLabel.setText("Peak ttl (ms)")
        self.falloffLabel.setText("Peak falloff (unit per time)")

    def set_configuration(self, conf):
        if(self.id in conf):
            self.intervalSpin.setValue(conf[self.id]["interval"] / 1000000)
            self.ttlSpin.setValue(conf[self.id]["peak-ttl"] / 1000000)
            self.falloffSpin.setValue(conf[self.id]["peak-falloff"])

    def get_configuration(self):
        conf = {self.id: {}}

        if not (self.groupBox.isCheckable() and not self.groupBox.isChecked()):
            conf[self.id]["interval"] = self.intervalSpin.value() * 1000000
            conf[self.id]["peak-ttl"] = self.ttlSpin.value() * 1000000
            conf[self.id]["peak-falloff"] = self.falloffSpin.value()

        return conf
