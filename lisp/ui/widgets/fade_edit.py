# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2017 Francesco Ceruti <ceppofrancy@gmail.com>
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
from PyQt5.QtWidgets import QDoubleSpinBox, QGridLayout, QLabel, QWidget

from lisp.ui.ui_utils import translate
from lisp.ui.widgets import FadeComboBox


class FadeEdit(QWidget):

    def __init__(self, *args, mode=FadeComboBox.Mode.FadeOut, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLayout(QGridLayout())

        self.fadeDurationSpin = QDoubleSpinBox(self)
        self.fadeDurationSpin.setRange(0, 3600)
        self.layout().addWidget(self.fadeDurationSpin, 0, 0)

        self.fadeDurationLabel = QLabel(self)
        self.fadeDurationLabel.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.fadeDurationLabel, 0, 1)

        self.fadeTypeCombo = FadeComboBox(self, mode=mode)
        self.layout().addWidget(self.fadeTypeCombo, 1, 0)

        self.fadeTypeLabel = QLabel(self)
        self.fadeTypeLabel.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.fadeTypeLabel, 1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.fadeDurationLabel.setText(translate('FadeEdit', 'Duration (sec)'))
        self.fadeTypeLabel.setText(translate('FadeEdit', 'Curve'))

    def duration(self):
        return self.fadeDurationSpin.value()

    def setDuration(self, value):
        self.fadeDurationSpin.setValue(value)

    def fadeType(self):
        return self.fadeTypeCombo.currentType()

    def setFadeType(self, fade_type):
        self.fadeTypeCombo.setCurrentType(fade_type)
