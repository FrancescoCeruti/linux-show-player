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

from lisp.ui.settings.pages import ConfigurationPage
from lisp.ui.ui_utils import translate


class CartLayoutSettings(ConfigurationPage):

    Name = 'Cart Layout'

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
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

        # Load data
        self.columnsSpin.setValue(config['grid.columns'])
        self.rowsSpin.setValue(config['grid.rows'])
        self.showSeek.setChecked(config['show.seekSliders'])
        self.showDbMeters.setChecked(config['show.dBMeters'])
        self.showAccurate.setChecked(config['show.accurateTime'])
        self.showVolume.setChecked(config['show.volumeControls'])
        self.countdownMode.setChecked(config['countdownMode'])
        self.autoAddPage.setChecked(config['autoAddPage'])

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

    def applySettings(self):
        self.config['grid.columns'] = self.columnsSpin.value()
        self.config['grid.rows'] = self.rowsSpin.value()
        self.config['show.dBMeters'] = self.showDbMeters.isChecked()
        self.config['show.seekSliders'] = self.showSeek.isChecked()
        self.config['show.accurateTime'] = self.showAccurate.isChecked()
        self.config['show.volumeControls'] = self.showVolume.isChecked()
        self.config['countdownMode'] = self.countdownMode.isChecked()
        self.config['autoAddPage'] = self.autoAddPage.isChecked()

        self.config.write()
