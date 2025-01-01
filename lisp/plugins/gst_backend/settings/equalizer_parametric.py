# This file is part of Linux Show Player
#
# Copyright 2024 Francesco Ceruti <ceppofrancy@gmail.com>
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
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QGroupBox, QTabWidget, QLabel, QDial, QGridLayout, QWidget, QVBoxLayout

from lisp.plugins.gst_backend.elements.equalizer_parametric import EqualizerParametric
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class EqualizerParametricSettings(SettingsPage):
    ELEMENT = EqualizerParametric
    Name = ELEMENT.Name

    bands = [
       {"gain": 0, "frequency": 60, "bandwidth": 0.3},
       {"gain": 0, "frequency": 250, "bandwidth": 0.3},
       {"gain": 0, "frequency": 3000, "bandwidth": 0.4},
       {"gain": 0, "frequency": 12000, "bandwidth": 0.5}
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.groupBox = QGroupBox()
        self.groupBox.resize(self.size())
        self.groupBox.setTitle(
            translate("Equalizer10Settings", "Parametric Equalizer")
        )
        self.groupBox.setLayout(QVBoxLayout())
        # self.groupBox.layout().setVerticalSpacing(0)
        self.layout().addWidget(self.groupBox)

        self.tabBox = QTabWidget()
        self.groupBox.layout().addWidget(self.tabBox)
        
        # Create tabs
        for i, b in enumerate(self.bands):
            tab = QWidget()
            self.tabBox.addTab(tab, "Band " + str(i))

        self.bands = {}

        # for n in range(10):
        #     label = QLabel(self.groupBox)
        #     label.setMinimumWidth(QFontMetrics(label.font()).width("000"))
        #     label.setAlignment(QtCore.Qt.AlignCenter)
        #     label.setNum(0)
        #     self.groupBox.layout().addWidget(label, 0, n)

        #     slider = QSlider(self.groupBox)
        #     slider.setRange(-24, 12)
        #     slider.setPageStep(1)
        #     slider.setValue(0)
        #     slider.setOrientation(QtCore.Qt.Vertical)
        #     slider.valueChanged.connect(label.setNum)
        #     self.groupBox.layout().addWidget(slider, 1, n)
        #     self.groupBox.layout().setAlignment(slider, QtCore.Qt.AlignHCenter)
        #     self.sliders["band" + str(n)] = slider

        #     fLabel = QLabel(self.groupBox)
        #     fLabel.setStyleSheet("font-size: 8pt;")
        #     fLabel.setAlignment(QtCore.Qt.AlignCenter)
        #     fLabel.setText(self.FREQ[n])
        #     self.groupBox.layout().addWidget(fLabel, 2, n)

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.groupBox, enabled)

    def getSettings(self):
        if self.isGroupEnabled(self.groupBox):
            return {}

        return {}
    
    
    # def loadSettings(self, settings):
    #     for band in self.sliders:
    #         # self.sliders[band].setValue(settings.get(band, 0))
class QEqBand(QWidget):
        def __init__(self, parent = ..., flags = ...):
            super().__init__(parent, flags)

            self.setLayout(QVBoxLayout())
            self.layout().setAlignment(Qt.AlignTop)

            self.groupBox = QGroupBox(self)
            self.groupBox.resize(self.size())
            self.groupBox.setTitle(
                translate("QEqBand", "Band")
            )
            self.groupBox.setLayout(QGridLayout())
            # self.groupBox.layout().setVerticalSpacing(0)
            self.layout().addWidget(self.groupBox)

            self.gain = QDial()
            self.gain.setRange(-90, 10)
            self.groupBox.layout().addWidget(self.gain, 0, 1, 1, 1)

            self.freq = QDial()
            self.freq.setRange(1, 20000)
            self.groupBox.layout().addWidget(self.freq, 1, 0, 1, 1)

            self.bandw = QDial()
            self.bandw.setRange(1, 20000)
            self.groupBox.layout().addWidget(self.bandw, 1, 1, 1, 1)
