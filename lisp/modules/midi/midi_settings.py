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

from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QComboBox, QMessageBox

from lisp.modules import check_module
from lisp.modules.midi.input_handler import MIDIInputHandler
from lisp.ui.settings.section import SettingsSection


class MIDISettings(SettingsSection):

    NAME = 'MIDI preferences'
    BACKENDS = {'RtMidi': 'mido.backends.rtmidi',
                'PortMidi': 'mido.backends.portmidi'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # MIDI Input
        self.inputGroup = QGroupBox(self)
        self.inputGroup.setTitle('Input MIDI device')
        self.inputGroup.setLayout(QVBoxLayout())
        self.inputGroup.setGeometry(0, 0, self.width(), 120)

        self.backendCombo = QComboBox(self.inputGroup)
        self.backendCombo.addItems(self.BACKENDS)
        self.backendCombo.currentTextChanged.connect(self._change_backend)
        self.inputGroup.layout().addWidget(self.backendCombo)

        self.deviceCombo = QComboBox(self.inputGroup)
        self.inputGroup.layout().addWidget(self.deviceCombo)

        self._load_devices()

    def get_configuration(self):
        conf = {}

        if self.backendCombo.isEnabled():
            conf['backend'] = self.BACKENDS[self.backendCombo.currentText()]
        if self.deviceCombo.isEnabled():
            conf['inputdevice'] = self.deviceCombo.currentText()
            MIDIInputHandler().change_port(conf['inputdevice'])

        return {'MIDI': conf}

    def set_configuration(self, conf):
        if 'backend' in conf['MIDI']:
            for backend in self.BACKENDS:
                if conf['MIDI']['backend'] == self.BACKENDS[backend]:
                    self.backendCombo.setCurrentText(backend)
                    break
        if 'inputdevice' in conf['MIDI']:
            self.deviceCombo.setCurrentText('default')
            # If the device is not found remains 'default'
            self.deviceCombo.setCurrentText(conf['MIDI']['inputdevice'])

    def _load_devices(self):
        if check_module('midi'):
            self.deviceCombo.clear()
            self.deviceCombo.addItem('default')
            self.deviceCombo.addItems(MIDIInputHandler().get_input_names())
        else:
            self.deviceCombo.setEnabled(False)

    def _change_backend(self, current):
        self.setEnabled(False)
        try:
            MIDIInputHandler().change_backend(self.BACKENDS[current])
            self._load_devices()
        except RuntimeError as e:
            QMessageBox.critical(self, 'Error', str(e))
        finally:
            self.setEnabled(True)
