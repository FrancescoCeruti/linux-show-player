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

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QGridLayout, \
    QDoubleSpinBox, QLabel, QComboBox, QStyledItemDelegate

from lisp.backends.gst.elements.fade import Fade
from lisp.backends.gst.settings.settings_page import GstElementSettingsPage


class FadeSettings(GstElementSettingsPage):
    NAME = "Fade"
    ELEMENT = Fade

    FadeOutIcons = {
        'Linear': QIcon.fromTheme('fadeout_linear'),
        'Quadratic': QIcon.fromTheme('fadeout_quadratic'),
        'Quadratic2': QIcon.fromTheme('fadeout_quadratic2')
    }

    FadeInIcons = {
        'Linear': QIcon.fromTheme('fadein_linear'),
        'Quadratic': QIcon.fromTheme('fadein_quadratic'),
        'Quadratic2': QIcon.fromTheme('fadein_quadratic2')
    }

    def __init__(self, element_id, **kwargs):
        super().__init__(element_id)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        # FadeIn
        self.fadeInGroup = QGroupBox(self)
        self.fadeInGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.fadeInGroup)

        self.fadeInSpin = QDoubleSpinBox(self.fadeInGroup)
        self.fadeInSpin.setMaximum(3600)
        self.fadeInGroup.layout().addWidget(self.fadeInSpin, 0, 0)

        self.fadeInLabel = QLabel(self.fadeInGroup)
        self.fadeInLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.fadeInGroup.layout().addWidget(self.fadeInLabel, 0, 1)

        self.fadeInCombo = QComboBox(self.fadeInGroup)
        self.fadeInCombo.setItemDelegate(QStyledItemDelegate())
        for key in sorted(self.FadeInIcons.keys()):
            self.fadeInCombo.addItem(self.FadeInIcons[key], key)
        self.fadeInGroup.layout().addWidget(self.fadeInCombo, 1, 0)

        self.fadeInExpLabel = QLabel(self.fadeInGroup)
        self.fadeInExpLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.fadeInGroup.layout().addWidget(self.fadeInExpLabel, 1, 1)

        # FadeOut
        self.fadeOutGroup = QGroupBox(self)
        self.fadeOutGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.fadeOutGroup)

        self.fadeOutSpin = QDoubleSpinBox(self.fadeOutGroup)
        self.fadeOutSpin.setMaximum(3600)
        self.fadeOutGroup.layout().addWidget(self.fadeOutSpin, 0, 0)

        self.fadeOutLabel = QLabel(self.fadeOutGroup)
        self.fadeOutLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.fadeOutGroup.layout().addWidget(self.fadeOutLabel, 0, 1)

        self.fadeOutCombo = QComboBox(self.fadeOutGroup)
        self.fadeOutCombo.setItemDelegate(QStyledItemDelegate())
        for key in sorted(self.FadeOutIcons.keys()):
            self.fadeOutCombo.addItem(self.FadeOutIcons[key], key)
        self.fadeOutGroup.layout().addWidget(self.fadeOutCombo, 1, 0)

        self.fadeOutExpLabel = QLabel(self.fadeOutGroup)
        self.fadeOutExpLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.fadeOutGroup.layout().addWidget(self.fadeOutExpLabel, 1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.fadeInGroup.setTitle("Fade In")
        self.fadeInLabel.setText("Time (sec)")
        self.fadeInExpLabel.setText("Exponent")
        self.fadeOutGroup.setTitle("Fade Out")
        self.fadeOutLabel.setText("Time (sec)")
        self.fadeOutExpLabel.setText("Exponent")

    def get_settings(self):
        conf = {self.id: {}}

        checkable = self.fadeInGroup.isCheckable()

        if not (checkable and not self.fadeInGroup.isChecked()):
            conf[self.id]["fadein"] = self.fadeInSpin.value()
            conf[self.id]["fadein_type"] = self.fadeInCombo.currentText()
        if not (checkable and not self.fadeOutGroup.isChecked()):
            conf[self.id]["fadeout"] = self.fadeOutSpin.value()
            conf[self.id]["fadeout_type"] = self.fadeOutCombo.currentText()

        return conf

    def load_settings(self, settings):
        if self.id in settings:
            settings = settings[self.id]

            self.fadeInSpin.setValue(settings["fadein"])
            self.fadeInCombo.setCurrentText(settings["fadein_type"])

            self.fadeOutSpin.setValue(settings["fadeout"])
            self.fadeOutCombo.setCurrentText(settings["fadeout_type"])

    def enable_check(self, enable):
        self.fadeInGroup.setCheckable(enable)
        self.fadeInGroup.setChecked(False)

        self.fadeOutGroup.setCheckable(enable)
        self.fadeOutGroup.setChecked(False)
