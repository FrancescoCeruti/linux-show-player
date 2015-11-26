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

from PyQt5 import QtCore
from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QTimeEdit, QLabel, \
    QSpinBox, QCheckBox, QVBoxLayout

from lisp.ui.settings.section import SettingsSection


class MediaCueSettings(SettingsSection):
    Name = 'Media Settings'

    def __init__(self, size, cue=None, parent=None):
        super().__init__(size, cue=cue, parent=parent)
        self.setLayout(QVBoxLayout(self))

        # Start at
        self.startGroup = QGroupBox(self)
        self.startGroup.setLayout(QHBoxLayout())

        self.startEdit = QTimeEdit(self.startGroup)
        self.startEdit.setDisplayFormat('HH.mm.ss.zzz')
        self.startGroup.layout().addWidget(self.startEdit)

        self.startLabel = QLabel(self.startGroup)
        self.startLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.startGroup.layout().addWidget(self.startLabel)

        self.layout().addWidget(self.startGroup)

        # Loop
        self.loopGroup = QGroupBox(self)
        self.loopGroup.setLayout(QHBoxLayout())

        self.spinLoop = QSpinBox(self.loopGroup)
        self.spinLoop.setRange(-1, 1000000)
        self.loopGroup.layout().addWidget(self.spinLoop)

        self.loopLabel = QLabel(self.loopGroup)
        self.loopLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.loopGroup.layout().addWidget(self.loopLabel)

        self.layout().addWidget(self.loopGroup)

        # Checks
        self.checkPause = QCheckBox(self)
        self.layout().addWidget(self.checkPause)

        self.retranslateUi()

    def retranslateUi(self):
        self.startGroup.setTitle('Start time')
        self.startLabel.setText('Amount of skip time')
        self.loopGroup.setTitle("Loop")
        self.loopLabel.setText("Repetition after first play (-1 = infinite)")
        self.checkPause.setText("Enable Pause")

    def get_configuration(self):
        conf = {'_media_': {}}
        checkable = self.startGroup.isCheckable()

        if not (checkable and not self.startGroup.isChecked()):
            time = self.startEdit.time().msecsSinceStartOfDay()
            conf['_media_']['start_at'] = time
        if not (checkable and not self.loopGroup.isChecked()):
            conf['_media_']['loop'] = self.spinLoop.value()
        if self.checkPause.checkState() != QtCore.Qt.PartiallyChecked:
            conf['pause'] = self.checkPause.isChecked()

        return conf

    def enable_check(self, enable):
        self.startGroup.setCheckable(enable)
        self.startGroup.setChecked(False)

        self.loopGroup.setCheckable(enable)
        self.loopGroup.setChecked(False)

        self.checkPause.setTristate(enable)
        if enable:
            self.checkPause.setCheckState(QtCore.Qt.PartiallyChecked)

    def set_configuration(self, conf):
        if 'pause' in conf:
            self.checkPause.setChecked(conf['pause'])
        if '_media_' in conf:
            if 'loop' in conf['_media_']:
                self.spinLoop.setValue(conf['_media_']['loop'])
            if conf['_media_'].get('duration', 0) > 0:
                t = self._to_qtime(conf['_media_']['duration'])
                self.startEdit.setMaximumTime(t)
            if 'start_at' in conf['_media_']:
                t = self._to_qtime(conf['_media_']['start_at'])
                self.startEdit.setTime(t)

    def _to_qtime(self, m_seconds):
        return QTime.fromMSecsSinceStartOfDay(m_seconds)