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
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QCheckBox, QComboBox, \
    QHBoxLayout, QLabel, QKeySequenceEdit, QGridLayout

from lisp.ui.settings.pages import ConfigurationPage
from lisp.ui.ui_utils import translate


class ListLayoutSettings(ConfigurationPage):
    Name = 'List Layout'

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.behaviorsGroup = QGroupBox(self)
        self.behaviorsGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.behaviorsGroup)

        self.showPlaying = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showPlaying)

        self.showDbMeters = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showDbMeters)

        self.showAccurate = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showAccurate)

        self.showSeek = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showSeek)

        self.autoNext = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.autoNext)

        self.goKeyLayout = QHBoxLayout()
        self.behaviorsGroup.layout().addLayout(self.goKeyLayout)
        self.goKeyLabel = QLabel(self.behaviorsGroup)
        self.goKeyLayout.addWidget(self.goKeyLabel)
        self.goKeyEdit = QKeySequenceEdit(self.behaviorsGroup)
        self.goKeyLayout.addWidget(self.goKeyEdit)
        self.goKeyLayout.setStretch(0, 2)
        self.goKeyLayout.setStretch(1, 5)

        self.useFadeGroup = QGroupBox(self)
        self.useFadeGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.useFadeGroup)

        # Fade settings
        self.stopCueFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.stopCueFade, 0, 0)
        self.pauseCueFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.pauseCueFade, 1, 0)
        self.resumeCueFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.resumeCueFade, 2, 0)
        self.interruptCueFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.interruptCueFade, 3, 0)

        self.retranslateUi()
        self.loadSettings()

    def retranslateUi(self):
        self.behaviorsGroup.setTitle(
            translate('ListLayout', 'Default behaviors'))
        self.showPlaying.setText(translate('ListLayout', 'Show playing cues'))
        self.showDbMeters.setText(translate('ListLayout', 'Show dB-meters'))
        self.showAccurate.setText(translate('ListLayout', 'Show accurate time'))
        self.showSeek.setText(translate('ListLayout', 'Show seek-bars'))
        self.autoNext.setText(translate('ListLayout', 'Auto-select next cue'))
        self.goKeyLabel.setText(translate('ListLayout', 'Go key:'))

        self.useFadeGroup.setTitle(
            translate('ListLayout', 'Use fade (buttons)'))
        self.stopCueFade.setText(translate('ListLayout', 'Stop Cue'))
        self.pauseCueFade.setText(translate('ListLayout', 'Pause Cue'))
        self.resumeCueFade.setText(translate('ListLayout', 'Resume Cue'))
        self.interruptCueFade.setText(translate('ListLayout', 'Interrupt Cue'))

    def loadSettings(self):
        self.showPlaying.setChecked(self.config['show.playingCues'])
        self.showDbMeters.setChecked(self.config['show.dBMeters'])
        self.showAccurate.setChecked(self.config['show.accurateTime'])
        self.showSeek.setChecked(self.config['show.seekSliders'])
        self.autoNext.setChecked(self.config['autoContinue'])
        self.goKeyEdit.setKeySequence(
            QKeySequence(self.config['goKey'], QKeySequence.NativeText))

        self.stopCueFade.setChecked(self.config['stopCueFade'])
        self.pauseCueFade.setChecked(self.config['pauseCueFade'])
        self.resumeCueFade.setChecked(self.config['resumeCueFade'])
        self.interruptCueFade.setChecked(self.config['interruptCueFade'])

    def applySettings(self):
        self.config['show.accurateTime'] = self.showAccurate.isChecked()
        self.config['show.playingCues'] = self.showPlaying.isChecked()
        self.config['show.dBMeters'] = self.showDbMeters.isChecked()
        self.config['show.seekBars'] = self.showSeek.isChecked()
        self.config['autoContinue'] = self.autoNext.isChecked()

        self.config['goKey'] = self.goKeyEdit.keySequence().toString(
            QKeySequence.NativeText)

        self.config['stopCueFade'] = self.stopCueFade.isChecked()
        self.config['pauseCueFade'] = self.pauseCueFade.isChecked()
        self.config['resumeCueFade'] = self.resumeCueFade.isChecked()
        self.config['interruptCueFade'] = self.interruptCueFade.isChecked()

        self.config.write()
