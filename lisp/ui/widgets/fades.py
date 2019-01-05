# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from enum import Enum

from PyQt5.QtCore import QT_TRANSLATE_NOOP, Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QStyledItemDelegate,
    QWidget,
    QGridLayout,
    QDoubleSpinBox,
    QLabel,
)

from lisp.ui.icons import IconTheme
from lisp.ui.ui_utils import translate

QT_TRANSLATE_NOOP("Fade", "Linear")
QT_TRANSLATE_NOOP("Fade", "Quadratic")
QT_TRANSLATE_NOOP("Fade", "Quadratic2")


class FadeComboBox(QComboBox):
    FadeOutIcons = {
        "Linear": "fadeout-linear",
        "Quadratic": "fadeout-quadratic",
        "Quadratic2": "fadeout-quadratic2",
    }

    FadeInIcons = {
        "Linear": "fadein-linear",
        "Quadratic": "fadein-quadratic",
        "Quadratic2": "fadein-quadratic2",
    }

    class Mode(Enum):
        FadeIn = 0
        FadeOut = 1

    def __init__(self, *args, mode=Mode.FadeOut, **kwargs):
        super().__init__(*args, **kwargs)
        self.setItemDelegate(QStyledItemDelegate())

        if mode == self.Mode.FadeIn:
            items = self.FadeInIcons
        else:
            items = self.FadeOutIcons

        for key in sorted(items.keys()):
            self.addItem(IconTheme.get(items[key]), translate("Fade", key), key)

    def setCurrentType(self, type):
        self.setCurrentText(translate("Fade", type))

    def currentType(self):
        return self.currentData()


class FadeEdit(QWidget):
    def __init__(self, *args, mode=FadeComboBox.Mode.FadeOut, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLayout(QGridLayout())

        self.fadeDurationLabel = QLabel(self)
        self.layout().addWidget(self.fadeDurationLabel, 0, 0)
        self.fadeDurationSpin = QDoubleSpinBox(self)
        self.fadeDurationSpin.setRange(0, 3600)
        self.layout().addWidget(self.fadeDurationSpin, 0, 1)

        self.fadeTypeLabel = QLabel(self)
        self.layout().addWidget(self.fadeTypeLabel, 1, 0)
        self.fadeTypeCombo = FadeComboBox(self, mode=mode)
        self.layout().addWidget(self.fadeTypeCombo, 1, 1)

        self.layout().setColumnStretch(0, 1)
        self.layout().setColumnStretch(1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.fadeDurationLabel.setText(translate("FadeEdit", "Duration (sec):"))
        self.fadeTypeLabel.setText(translate("FadeEdit", "Curve:"))

    def duration(self):
        return self.fadeDurationSpin.value()

    def setDuration(self, value):
        self.fadeDurationSpin.setValue(value)

    def fadeType(self):
        return self.fadeTypeCombo.currentType()

    def setFadeType(self, fade_type):
        self.fadeTypeCombo.setCurrentType(fade_type)
