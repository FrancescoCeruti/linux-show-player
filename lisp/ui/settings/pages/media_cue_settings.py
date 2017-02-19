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

from PyQt5.QtCore import QTime, Qt
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QTimeEdit, QLabel, \
    QSpinBox, QVBoxLayout

from lisp.ui.settings.settings_page import SettingsPage
from lisp.ui.ui_utils import translate


class MediaCueSettings(SettingsPage):
    Name = 'Media-Cue'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout(self))

        # Start time
        self.startGroup = QGroupBox(self)
        self.startGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.startGroup)

        self.startEdit = QTimeEdit(self.startGroup)
        self.startEdit.setDisplayFormat('HH.mm.ss.zzz')
        self.startGroup.layout().addWidget(self.startEdit)

        self.startLabel = QLabel(self.startGroup)
        self.startLabel.setAlignment(Qt.AlignCenter)
        self.startGroup.layout().addWidget(self.startLabel)

        # Stop time
        self.stopGroup = QGroupBox(self)
        self.stopGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.stopGroup)

        self.stopEdit = QTimeEdit(self.stopGroup)
        self.stopEdit.setDisplayFormat('HH.mm.ss.zzz')
        self.stopGroup.layout().addWidget(self.stopEdit)

        self.stopLabel = QLabel(self.stopGroup)
        self.stopLabel.setAlignment(Qt.AlignCenter)
        self.stopGroup.layout().addWidget(self.stopLabel)

        # Loop
        self.loopGroup = QGroupBox(self)
        self.loopGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.loopGroup)

        self.spinLoop = QSpinBox(self.loopGroup)
        self.spinLoop.setRange(-1, 1000000)
        self.loopGroup.layout().addWidget(self.spinLoop)

        self.loopLabel = QLabel(self.loopGroup)
        self.loopLabel.setAlignment(Qt.AlignCenter)
        self.loopGroup.layout().addWidget(self.loopLabel)

        self.retranslateUi()

    def retranslateUi(self):
        self.startGroup.setTitle(translate('MediaCueSettings', 'Start time'))
        self.stopLabel.setText(
            translate('MediaCueSettings', 'Stop position of the media'))
        self.stopGroup.setTitle(translate('MediaCueSettings', 'Stop time'))
        self.startLabel.setText(
            translate('MediaCueSettings', 'Start position of the media'))
        self.loopGroup.setTitle(translate('MediaCueSettings', 'Loop'))
        self.loopLabel.setText(
            translate('MediaCueSettings', 'Repetition after first play '
                                          '(-1 = infinite)'))

    def get_settings(self):
        conf = {'_media_': {}}
        checkable = self.startGroup.isCheckable()

        if not (checkable and not self.startGroup.isChecked()):
            time = self.startEdit.time().msecsSinceStartOfDay()
            conf['_media_']['start_time'] = time
        if not (checkable and not self.stopGroup.isChecked()):
            time = self.stopEdit.time().msecsSinceStartOfDay()
            conf['_media_']['stop_time'] = time
        if not (checkable and not self.loopGroup.isChecked()):
            conf['_media_']['loop'] = self.spinLoop.value()

        return conf

    def enable_check(self, enable):
        self.startGroup.setCheckable(enable)
        self.startGroup.setChecked(False)

        self.stopGroup.setCheckable(enable)
        self.stopGroup.setChecked(False)

        self.loopGroup.setCheckable(enable)
        self.loopGroup.setChecked(False)

    def load_settings(self, settings):
        if '_media_' in settings:
            if 'loop' in settings['_media_']:
                self.spinLoop.setValue(settings['_media_']['loop'])
            if 'start_time' in settings['_media_']:
                t = self._to_qtime(settings['_media_']['start_time'])
                self.startEdit.setTime(t)
            if 'stop_time' in settings['_media_']:
                t = self._to_qtime(settings['_media_']['stop_time'])
                self.stopEdit.setTime(t)

            t = self._to_qtime(settings['_media_'].get('duration', 0))
            self.startEdit.setMaximumTime(t)
            self.stopEdit.setMaximumTime(t)

    def _to_qtime(self, m_seconds):
        return QTime.fromMSecsSinceStartOfDay(m_seconds)
