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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QCheckBox, QGridLayout, \
    QSpinBox, QLabel

from lisp.ui.settings.settings_page import SettingsPage
from lisp.ui.ui_utils import translate


class CartLayoutSettings(SettingsPage):

    Name = 'Cart Layout'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.behaviorsGroup = QGroupBox(self)
        self.behaviorsGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.behaviorsGroup)

        self.countdownMode = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.countdownMode)

        self.showSeek = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showSeek)

        self.showDbMeters = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showDbMeters)

        self.showAccurate = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showAccurate)

        self.showVolume = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showVolume)

        self.autoAddPage = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.autoAddPage)

        self.gridSizeGroup = QGroupBox(self)
        self.gridSizeGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.gridSizeGroup)

        self.columnsSpin = QSpinBox(self.gridSizeGroup)
        self.columnsSpin.setRange(1, 16)
        self.gridSizeGroup.layout().addWidget(self.columnsSpin, 0, 0)

        self.columnsLabel = QLabel(self.gridSizeGroup)
        self.gridSizeGroup.layout().addWidget(self.columnsLabel, 0, 1)

        self.rowsSpin = QSpinBox(self.gridSizeGroup)
        self.rowsSpin.setRange(1, 16)
        self.gridSizeGroup.layout().addWidget(self.rowsSpin, 1, 0)

        self.rowsLabel = QLabel(self.gridSizeGroup)
        self.gridSizeGroup.layout().addWidget(self.rowsLabel, 1, 1)

        self.gridSizeGroup.layout().setColumnStretch(0, 5)
        self.gridSizeGroup.layout().setColumnStretch(1, 3)

        self.retranslateUi()

    def retranslateUi(self):
        self.behaviorsGroup.setTitle(
            translate('CartLayout', 'Default behaviors'))
        self.countdownMode.setText(translate('CartLayout', 'Countdown mode'))
        self.showSeek.setText(translate('CartLayout', 'Show seek-bars'))
        self.showDbMeters.setText(translate('CartLayout', 'Show dB-meters'))
        self.showAccurate.setText(translate('CartLayout', 'Show accurate time'))
        self.showVolume.setText(translate('CartLayout', 'Show volume'))
        self.autoAddPage.setText(
            translate('CartLayout', 'Automatically add new page'))
        self.gridSizeGroup.setTitle(translate('CartLayout', 'Grid size'))
        self.columnsLabel.setText(translate('CartLayout', 'Number of columns'))
        self.rowsLabel.setText(translate('CartLayout', 'Number of rows'))

    def get_settings(self):
        conf = {
            'GridColumns': self.columnsSpin.value(),
            'GridRows': self.rowsSpin.value(),
            'ShowDbMeters': self.showDbMeters.isChecked(),
            'ShowSeek': self.showSeek.isChecked(),
            'ShowAccurate': self.showAccurate.isChecked(),
            'ShowVolume': self.showVolume.isChecked(),
            'Countdown': self.countdownMode.isChecked(),
            'AutoAddPage': self.autoAddPage.isChecked()
        }

        return {'CartLayout': conf}

    def load_settings(self, settings):
        settings = settings.get('CartLayout', {})

        self.columnsSpin.setValue(settings['GridColumns'])
        self.rowsSpin.setValue(settings['GridRows'])
        self.showSeek.setChecked(settings['ShowSeek'])
        self.showDbMeters.setChecked(settings['ShowDbMeters'])
        self.showAccurate.setChecked(settings['ShowAccurate'])
        self.showVolume.setChecked(settings['ShowVolume'])
        self.countdownMode.setChecked(settings['Countdown'])
        self.autoAddPage.setChecked(settings['AutoAddPage'])
