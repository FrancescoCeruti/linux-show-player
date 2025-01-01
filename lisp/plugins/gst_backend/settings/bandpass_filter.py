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
from PyQt5.QtWidgets import QGroupBox, QGridLayout, QLabel, QSlider, QVBoxLayout, QComboBox

from lisp.plugins.gst_backend.elements.bandpass_filter import BandpassFilter
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class BandpassFilterSettings(SettingsPage):
    ELEMENT = BandpassFilter
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.groupBox = QGroupBox(self)
        self.groupBox.resize(self.size())
        self.groupBox.setTitle(
            translate("BandpassFilterSettings", "Bandpass Filter")
        )
        self.groupBox.setLayout(QGridLayout())
        self.groupBox.layout().setVerticalSpacing(0)
        self.layout().addWidget(self.groupBox)

        self.sliders = {}

        
         # Low-freq
        lLabel = QLabel(self.groupBox)
        lLabel.setMinimumWidth(QFontMetrics(lLabel.font()).width("000"))
        lLabel.setAlignment(QtCore.Qt.AlignCenter)
        lLabel.setNum(0)
        self.groupBox.layout().addWidget(lLabel, 0, 0)

        slider = QSlider(self.groupBox)
        slider.setRange(0, 20000)
        slider.setPageStep(1)
        slider.setValue(0)
        slider.setOrientation(QtCore.Qt.Horizontal)
        slider.valueChanged.connect(lLabel.setNum)
        self.groupBox.layout().addWidget(slider, 1, 0)
        self.groupBox.layout().setAlignment(slider, QtCore.Qt.AlignVCenter)
        self.sliders["lofreq"] = slider

        fLabel = QLabel(self.groupBox)
        fLabel.setStyleSheet("font-size: 8pt;")
        fLabel.setAlignment(QtCore.Qt.AlignCenter)
        fLabel.setText(translate("BandpassFilterSettings", "Lower Frequency"))
        self.groupBox.layout().addWidget(fLabel, 3, 0)

        # High-freq
        hLabel = QLabel(self.groupBox)
        hLabel.setMinimumWidth(QFontMetrics(hLabel.font()).width("000"))
        hLabel.setAlignment(QtCore.Qt.AlignCenter)
        hLabel.setNum(0)
        self.groupBox.layout().addWidget(hLabel, 4, 0)

        slider2 = QSlider(self.groupBox)
        slider2.setRange(0, 20000)
        slider2.setPageStep(1)
        slider2.setValue(20000)
        slider2.setOrientation(QtCore.Qt.Horizontal)
        slider2.valueChanged.connect(hLabel.setNum)
        self.groupBox.layout().addWidget(slider2, 5, 0)
        self.groupBox.layout().setAlignment(slider2, QtCore.Qt.AlignVCenter)
        self.sliders["hifreq"] = slider2

        fLabel = QLabel(self.groupBox)
        fLabel.setStyleSheet("font-size: 8pt;")
        fLabel.setAlignment(QtCore.Qt.AlignCenter)
        fLabel.setText(translate("BandpassFilterSettings", "Upper Frequency"))
        self.groupBox.layout().addWidget(fLabel, 6, 0)

        # Window mode
        self.windowComboBox = QComboBox(self.groupBox)
        self.windowComboBox.addItem(
            translate("BandpassFilterSettings", "Hamming"), 'hamming'
        )
        self.windowComboBox.addItem(
            translate("BandpassFilterSettings", "Blackman"), 'blackman'
        )
        self.windowComboBox.addItem(
            translate("BandpassFilterSettings", "Gaussian"), 'gaussian'
        )
        self.windowComboBox.addItem(
            translate("BandpassFilterSettings", "Cosine"), 'cosine'
        )
        self.windowComboBox.addItem(
            translate("BandpassFilterSettings", "Hann"), 'hann'
        )

        self.groupBox.layout().addWidget(self.windowComboBox, 7, 0, 1, 1)
        
        wLabel = QLabel(self.groupBox)
        wLabel.setStyleSheet("font-size: 8pt;")
        wLabel.setAlignment(QtCore.Qt.AlignCenter)
        wLabel.setText(translate("BandpassFilterSettings", "Window Mode"))
        self.groupBox.layout().addWidget(wLabel, 8, 0)

        # Filter mode
        self.modeComboBox = QComboBox(self.groupBox)
        self.modeComboBox.addItem(
            translate("BandpassFilterSettings", "Band-Pass"), 'band-pass'
        )
        self.modeComboBox.addItem(
            translate("BandpassFilterSettings", "Band-Reject"), 'band-reject'
        )

        self.groupBox.layout().addWidget(self.modeComboBox, 9, 0, 1, 1)
        
        mLabel = QLabel(self.groupBox)
        mLabel.setStyleSheet("font-size: 8pt;")
        mLabel.setAlignment(QtCore.Qt.AlignCenter)
        mLabel.setText(translate("BandpassFilterSettings", "Filter Mode"))
        self.groupBox.layout().addWidget(mLabel, 10, 0)

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.groupBox, enabled)

    def getSettings(self):
        if self.isGroupEnabled(self.groupBox):
            return {
                'hiFreq': self.sliders['hifreq'].value(),
                'loFreq': self.sliders['lofreq'].value(),
                'window': self.windowComboBox.currentData(),
                'mode': self.modeComboBox.currentData()
            }

        return {}

    def loadSettings(self, settings):
        self.sliders['hifreq'].setValue(settings.get('hiFreq', 200000))
        self.sliders['lofreq'].setValue(settings.get('loFreq', 1))
        self.modeComboBox.setCurrentText(
            translate("BandpassFilterSettings", str(settings.get('mode', 'band-pass')).title())
        )
        self.windowComboBox.setCurrentText(
            translate("BandpassFilterSettings", str(settings.get('window', 'hamming')).title())
        )

