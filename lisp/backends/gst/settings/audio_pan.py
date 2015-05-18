# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QSlider, QLabel

from lisp.backends.gst.elements.audio_pan import AudioPan
from lisp.ui.settings.section import SettingsSection


class AudioPanSettings(SettingsSection):

    NAME = "Pan"
    ELEMENT = AudioPan

    def __init__(self, size, Id, parent=None):
        super().__init__(size, parent)

        self.id = Id

        self.panBox = QGroupBox(self)
        self.panBox.setGeometry(0, 0, self.width(), 80)
        self.panBox.setLayout(QHBoxLayout(self.panBox))

        self.panSlider = QSlider(self.panBox)
        self.panSlider.setRange(-10, 10)
        self.panSlider.setPageStep(1)
        self.panSlider.setOrientation(Qt.Horizontal)
        self.panSlider.valueChanged.connect(self.pan_changed)
        self.panBox.layout().addWidget(self.panSlider)

        self.panLabel = QLabel(self.panBox)
        self.panLabel.setAlignment(Qt.AlignCenter)
        self.panBox.layout().addWidget(self.panLabel)

        self.panBox.layout().setStretch(0, 5)
        self.panBox.layout().setStretch(1, 1)

        self.retransaleUi()

    def retransaleUi(self):
        self.panBox.setTitle("Audio Pan")
        self.panLabel.setText("Center")

    def enable_check(self, enable):
        self.panBox.setCheckable(enable)
        self.panBox.setChecked(False)

    def get_configuration(self):
        conf = {}

        if not (self.panBox.isCheckable() and not self.panBox.isChecked()):
            conf["panorama"] = self.panSlider.value() / 10

        return {self.id: conf}

    def set_configuration(self, conf):
        if conf is not None and self.id in conf:
            self.panSlider.setValue(conf[self.id]["panorama"] * 10)

    def pan_changed(self, value):
        if value < 0:
            self.panLabel.setText("Left")
        elif value > 0:
            self.panLabel.setText("Right")
        else:
            self.panLabel.setText("Center")
