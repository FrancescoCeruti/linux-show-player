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

from PyQt5.QtCore import QT_TRANSLATE_NOOP, Qt
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QLabel,\
    QCheckBox, QComboBox, QHBoxLayout

from lisp.ui.settings.settings_page import CueSettingsPage


class TimecodeSettings(CueSettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'Timecode')

    def __init__(self, cue_class, **kwargs):
        super().__init__(cue_class, **kwargs)
        self.setLayout(QVBoxLayout())

        groupbox = QGroupBox(self)
        groupbox.setLayout(QVBoxLayout())
        groupbox.setAlignment(Qt.AlignTop)
        groupbox.setTitle("Timecode")
        self.layout().addWidget(groupbox)

        label = QLabel("to send ArtNet Timecode you need to setup a running OLA session!")
        groupbox.layout().addWidget(label)

        # enable / disable timecode
        self.tc_enable = QCheckBox("send ArtNet Timecode")
        self.tc_enable.setChecked(False)
        groupbox.layout().addWidget(self.tc_enable)

        # Hours can be replaced by cue number h:m:s:frames -> CUE:m:s:frames
        self.tc_usehours = QCheckBox("replace HOURS by cue index")
        self.tc_usehours.setChecked(True)
        groupbox.layout().addWidget(self.tc_usehours)

        # TimeCode Format: FILM, EBU, SMPTE
        hbox = QHBoxLayout()
        self.tc_format = QComboBox()
        self.tc_format.addItem("FILM")
        self.tc_format.addItem("EBU")
        self.tc_format.addItem("SMPTE")
        hbox.layout().addWidget(self.tc_format)
        label = QLabel("Choose Timecode Format")
        hbox.layout().addWidget(label)
        groupbox.layout().addLayout(hbox)

    def get_settings(self):
        conf = dict()
        conf['enabled'] = self.tc_enable.isChecked()
        conf['use_hours'] = self.tc_usehours.isChecked()
        conf['format'] = self.tc_format.currentIndex()
        return {'timecode': conf}

    def load_settings(self, settings):
        if settings is not None and 'timecode' in settings:
            conf = settings['timecode']
            if 'enabled' in conf:
                self.tc_enable.setChecked(conf['enabled'])
            if 'use_hours' in conf:
                self.tc_usehours.setChecked(conf['use_hours'])
            if 'format' in conf:
                self.tc_format.setCurrentIndex(conf['format'])