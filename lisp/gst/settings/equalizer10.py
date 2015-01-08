##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5 import QtCore
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import *  # @UnusedWildImport

from lisp.gst.elements.equalizer10 import Equalizer10
from lisp.ui.qvertiacallabel import QVerticalLabel
from lisp.ui.settings.section import SettingsSection


class Equalizer10Settings(SettingsSection):

    NAME = "Equalizer"
    ELEMENT = Equalizer10

    FREQ = ["30Hz", "60Hz", "120Hz", "240Hz", "475Hz", "950Hz", "1900Hz",
            "3800Hz", "7525Hz", "15KHz"]

    def __init__(self, size, Id, parent=None):
        super().__init__(size, parent)

        self.id = Id

        self.groupBox = QGroupBox(self)
        self.groupBox.resize(self.size())
        self.groupBox.setTitle("10 Bands Equalizer (IIR)")

        self.gridLayout = QGridLayout(self.groupBox)

        self.sliders = {}

        for n in range(10):
            label = QLabel(self.groupBox)
            width = QFontMetrics(label.font()).width('000')
            label.setMinimumWidth(width)
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setNum(0)
            self.gridLayout.addWidget(label, 0, n)

            slider = QSlider(self.groupBox)
            slider.setMinimum(-24)
            slider.setMaximum(12)
            slider.setPageStep(1)
            slider.setValue(0)
            slider.setOrientation(QtCore.Qt.Vertical)
            slider.valueChanged.connect(label.setNum)
            self.gridLayout.addWidget(slider, 1, n)
            self.gridLayout.setAlignment(slider, QtCore.Qt.AlignHCenter)
            self.sliders["band" + str(n)] = slider

            fLabel = QVerticalLabel(self.groupBox)
            fLabel.setAlignment(QtCore.Qt.AlignCenter)
            fLabel.setText(self.FREQ[n])
            self.gridLayout.addWidget(fLabel, 2, n)

        self.gridLayout.setRowStretch(0, 1)
        self.gridLayout.setRowStretch(1, 10)
        self.gridLayout.setRowStretch(2, 1)

    def enable_check(self, enable):
        self.groupBox.setCheckable(enable)
        self.groupBox.setChecked(False)

    def get_configuration(self):
        conf = {}

        if not (self.groupBox.isCheckable() and not self.groupBox.isChecked()):
            conf[self.id] = {}
            for band in self.sliders:
                conf[self.id][band] = self.sliders[band].value()

        return conf

    def set_configuration(self, conf):
        if(conf is not None):
            if(self.id in conf):
                for band in self.sliders:
                    if(band in conf[self.id]):
                        self.sliders[band].setValue(conf[self.id][band])
