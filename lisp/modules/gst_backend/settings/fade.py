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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QGridLayout, QLabel, \
    QDoubleSpinBox, QComboBox, QStyledItemDelegate

from lisp.modules.gst_backend.elements.fade import Fade
from lisp.ui.settings.settings_page import SettingsPage
from lisp.ui.ui_utils import translate


class FadeSettings(SettingsPage):
    ELEMENT = Fade
    Name = ELEMENT.Name

    FadeOutIcons = {
        QT_TRANSLATE_NOOP('FadeSettings', 'Linear'):
            QIcon.fromTheme('fadeout_linear'),
        QT_TRANSLATE_NOOP('FadeSettings', 'Quadratic'):
            QIcon.fromTheme('fadeout_quadratic'),
        QT_TRANSLATE_NOOP('FadeSettings', 'Quadratic2'):
            QIcon.fromTheme('fadeout_quadratic2')
    }

    FadeInIcons = {
        'Linear': QIcon.fromTheme('fadein_linear'),
        'Quadratic': QIcon.fromTheme('fadein_quadratic'),
        'Quadratic2': QIcon.fromTheme('fadein_quadratic2')
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
        self.fadeInLabel.setAlignment(Qt.AlignCenter)
        self.fadeInGroup.layout().addWidget(self.fadeInLabel, 0, 1)

        self.fadeInCombo = QComboBox(self.fadeInGroup)
        self.fadeInCombo.setItemDelegate(QStyledItemDelegate())
        for key in sorted(self.FadeInIcons.keys()):
            self.fadeInCombo.addItem(self.FadeInIcons[key],
                                     translate('FadeSettings', key),
                                     key)
        self.fadeInGroup.layout().addWidget(self.fadeInCombo, 1, 0)

        self.fadeInExpLabel = QLabel(self.fadeInGroup)
        self.fadeInExpLabel.setAlignment(Qt.AlignCenter)
        self.fadeInGroup.layout().addWidget(self.fadeInExpLabel, 1, 1)

        # FadeOut
        self.fadeOutGroup = QGroupBox(self)
        self.fadeOutGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.fadeOutGroup)

        self.fadeOutSpin = QDoubleSpinBox(self.fadeOutGroup)
        self.fadeOutSpin.setMaximum(3600)
        self.fadeOutGroup.layout().addWidget(self.fadeOutSpin, 0, 0)

        self.fadeOutLabel = QLabel(self.fadeOutGroup)
        self.fadeOutLabel.setAlignment(Qt.AlignCenter)
        self.fadeOutGroup.layout().addWidget(self.fadeOutLabel, 0, 1)

        self.fadeOutCombo = QComboBox(self.fadeOutGroup)
        self.fadeOutCombo.setItemDelegate(QStyledItemDelegate())
        for key in sorted(self.FadeOutIcons.keys()):
            self.fadeOutCombo.addItem(self.FadeOutIcons[key],
                                      translate('FadeSettings', key),
                                      key)
        self.fadeOutGroup.layout().addWidget(self.fadeOutCombo, 1, 0)

        self.fadeOutExpLabel = QLabel(self.fadeOutGroup)
        self.fadeOutExpLabel.setAlignment(Qt.AlignCenter)
        self.fadeOutGroup.layout().addWidget(self.fadeOutExpLabel, 1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.fadeInGroup.setTitle(translate('FadeSettings', 'Fade In'))
        self.fadeInLabel.setText(translate('FadeSettings', 'Duration (sec)'))
        self.fadeInExpLabel.setText(translate('FadeSettings', 'Curve'))
        self.fadeOutGroup.setTitle(translate('FadeSettings', 'Fade Out'))
        self.fadeOutLabel.setText(translate('FadeSettings', 'Duration (sec)'))
        self.fadeOutExpLabel.setText(translate('FadeSettings', 'Curve'))

    def get_settings(self):
        settings = {}

        checkable = self.fadeInGroup.isCheckable()

        if not (checkable and not self.fadeInGroup.isChecked()):
            settings['fadein'] = self.fadeInSpin.value()
            settings['fadein_type'] = self.fadeInCombo.currentData()
        if not (checkable and not self.fadeOutGroup.isChecked()):
            settings['fadeout'] = self.fadeOutSpin.value()
            settings['fadeout_type'] = self.fadeOutCombo.currentData()

        return settings

    def load_settings(self, settings):
        self.fadeInSpin.setValue(settings.get('fadein', 0))
        self.fadeInCombo.setCurrentText(
            translate('FadeSettings', settings.get('fadein_type', '')))

        self.fadeOutSpin.setValue(settings.get('fadeout', 0))
        self.fadeOutCombo.setCurrentText(
            translate('FadeSettings', settings.get('fadeout_type', '')))

    def enable_check(self, enable):
        self.fadeInGroup.setCheckable(enable)
        self.fadeInGroup.setChecked(False)

        self.fadeOutGroup.setCheckable(enable)
        self.fadeOutGroup.setChecked(False)
