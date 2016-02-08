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
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QComboBox, QApplication

from lisp.modules import check_module
from lisp.modules.midi.input_handler import MIDIInputHandler
from lisp.ui.settings.settings_page import SettingsPage
from lisp.utils import logging


class MIDISettings(SettingsPage):

    NAME = 'MIDI settings'
    BACKENDS = {'RtMidi': 'mido.backends.rtmidi',
                'PortMidi': 'mido.backends.portmidi'}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        # MIDI Input
        self.inputGroup = QGroupBox(self)
        self.inputGroup.setTitle('MIDI input device')
        self.inputGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.inputGroup)

        self.backendCombo = QComboBox(self.inputGroup)
        self.backendCombo.addItems(self.BACKENDS)
        self.backendCombo.currentTextChanged.connect(self._change_backend)
        self.inputGroup.layout().addWidget(self.backendCombo)

        self.deviceCombo = QComboBox(self.inputGroup)
        self.inputGroup.layout().addWidget(self.deviceCombo)

        self._load_devices()

    def get_settings(self):
        conf = {}

        if self.backendCombo.isEnabled():
            conf['backend'] = self.BACKENDS[self.backendCombo.currentText()]
        if self.deviceCombo.isEnabled():
            conf['inputdevice'] = self.deviceCombo.currentText()
            MIDIInputHandler().change_port(conf['inputdevice'])

        return {'MIDI': conf}

    def load_settings(self, settings):
        if 'backend' in settings['MIDI']:
            for backend in self.BACKENDS:
                if settings['MIDI']['backend'] == self.BACKENDS[backend]:
                    self.backendCombo.setCurrentText(backend)
                    break
        if 'inputdevice' in settings['MIDI']:
            self.deviceCombo.setCurrentText('default')
            # If the device is not found remains 'default'
            self.deviceCombo.setCurrentText(settings['MIDI']['inputdevice'])

    def _load_devices(self):
        if check_module('Midi'):
            self.deviceCombo.clear()
            self.deviceCombo.addItem('default')
            self.deviceCombo.addItems(MIDIInputHandler().get_input_names())
        else:
            self.deviceCombo.setEnabled(False)

    def _change_backend(self, current):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.setEnabled(False)

        try:
            MIDIInputHandler().change_backend(self.BACKENDS[current])
            self._load_devices()
        except RuntimeError as e:
            logging.exception('Failed to load the backend', e, dialog=True)
        finally:
            QApplication.restoreOverrideCursor()
            self.setEnabled(True)