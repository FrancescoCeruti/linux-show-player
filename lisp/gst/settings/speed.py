##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5 import QtCore
from PyQt5.QtWidgets import *  # @UnusedWildImport

from lisp.gst.elements.speed import Speed
from lisp.ui.settings.section import SettingsSection


class SpeedSettings(SettingsSection):

    NAME = 'Speed'
    ELEMENT = Speed

    def __init__(self, size, Id, parent=None):
        super().__init__(size, parent)

        self.id = Id

        self.groupBox = QGroupBox(self)
        self.groupBox.setGeometry(0, 0, self.width(), 80)

        self.layout = QHBoxLayout(self.groupBox)

        self.speedSlider = QSlider(self.groupBox)
        self.speedSlider.setMinimum(1)
        self.speedSlider.setMaximum(1000)
        self.speedSlider.setPageStep(1)
        self.speedSlider.setValue(100)
        self.speedSlider.setOrientation(QtCore.Qt.Horizontal)
        self.speedSlider.setTickPosition(QSlider.TicksAbove)
        self.speedSlider.setTickInterval(10)
        self.layout.addWidget(self.speedSlider)

        self.speedLabel = QLabel(self.groupBox)
        self.speedLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.speedLabel)

        self.layout.setStretch(0, 3)
        self.layout.setStretch(1, 1)

        self.speedSlider.valueChanged.connect(self.speedChanged)

        self.retranslateUi()

    def retranslateUi(self):
        self.groupBox.setTitle("Speed")
        self.speedLabel.setText("1.0")

    def enable_check(self, enable):
        self.groupBox.setCheckable(enable)
        self.groupBox.setChecked(False)

    def get_configuration(self):
        conf = {}

        if not (self.groupBox.isCheckable() and not self.groupBox.isChecked()):
            conf[self.id] = {'speed': self.speedSlider.value() / 100}

        return conf

    def set_configuration(self, conf):
        if conf is not None and self.id in conf:
            self.speedSlider.setValue(conf[self.id]['speed'] * 100)

    def speedChanged(self, value):
        self.speedLabel.setText(str(value / 100.0))
