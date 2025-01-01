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
from PyQt5.QtWidgets import (
    QGroupBox,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QSpinBox
)
from lisp.plugins.gst_backend.elements.audio_echo import AudioEcho
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class AudioEchoSettings(SettingsPage):
    ELEMENT = AudioEcho
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.groupBox = QGroupBox(self)
        self.groupBox.resize(self.size())
        self.groupBox.setTitle(
            translate("AudioEchoSettings", "Echo Settings")
        )
        self.groupBox.setLayout(QGridLayout())
        self.groupBox.layout().setVerticalSpacing(10)
        self.layout().addWidget(self.groupBox)

        # Delay time (ms)
        self.delaySpin = QSpinBox(self.groupBox)
        self.delaySpin.setRange(1, 5000)
        self.delaySpin.setMaximum(5000)
        self.delaySpin.setValue(300)
        self.delaySpin.setSuffix(" ms")
        self.groupBox.layout().addWidget(self.delaySpin, 0, 0, 1, 1)

        dLabel = QLabel(self.groupBox)
        dLabel.setAlignment(QtCore.Qt.AlignCenter)
        dLabel.setText(translate("AudioEchoSettings", "Delay time (ms)"))
        self.groupBox.layout().addWidget(dLabel, 0, 1, 1, 1)


        # Feedback
        self.feedbackSpin = QSpinBox(self.groupBox)
        self.feedbackSpin.setRange(1, 100)
        self.feedbackSpin.setMaximum(100)
        self.feedbackSpin.setValue(20)
        self.feedbackSpin.stepBy(10)
        self.groupBox.layout().addWidget(self.feedbackSpin, 1, 0, 1, 1)

        fLabel = QLabel(self.groupBox)
        fLabel.setAlignment(QtCore.Qt.AlignCenter)
        fLabel.setText(translate("AudioEchoSettings", "Feedback"))
        self.groupBox.layout().addWidget(fLabel, 1, 1, 1, 1)


        # Intensity
        self.intensitySpin = QSpinBox(self.groupBox)
        self.intensitySpin.setRange(1, 100)
        self.intensitySpin.setMaximum(100)
        self.intensitySpin.setValue(40)
        self.intensitySpin.stepBy(10)
        self.groupBox.layout().addWidget(self.intensitySpin, 2, 0, 1, 1)

        iLabel = QLabel(self.groupBox)
        iLabel.setAlignment(QtCore.Qt.AlignCenter)
        iLabel.setText(translate("AudioEchoSettings", "Intensity"))
        self.groupBox.layout().addWidget(iLabel, 2, 1, 1, 1)


    def enableCheck(self, enabled):
        self.setGroupEnabled(self.groupBox, enabled)

    def getSettings(self):
        if self.isGroupEnabled(self.groupBox):
            return {
                'delay': self.delaySpin.value() * 1e6,
                'feedback': float(self.feedbackSpin.value() / 100),
                'intensity': float(self.intensitySpin.value() / 100),
            }

        return {}

    def loadSettings(self, settings):
        self.delaySpin.setValue(int(settings.get('delay', 300) / 1e6))
        self.feedbackSpin.setValue(int(settings.get('feedback', 0.0) * 100))
        self.intensitySpin.setValue(int(settings.get('intensity', 0.0) * 100))

