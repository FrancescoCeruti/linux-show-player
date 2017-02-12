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
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QComboBox, QGridLayout, QLabel

from lisp.modules import check_module
from lisp.modules.midi.midi_input import MIDIInput
from lisp.modules.midi.midi_output import MIDIOutput
from lisp.modules.midi.midi_utils import mido_backend
from lisp.ui.settings.settings_page import SettingsPage
from lisp.ui.ui_utils import translate


class MIDISettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'MIDI settings')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.midiGroup = QGroupBox(self)
        self.midiGroup.setTitle(
            translate('MIDISettings', 'MIDI default devices'))
        self.midiGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.midiGroup)

        self.inputLabel = QLabel(translate('MIDISettings', 'Input'),
                                 self.midiGroup)
        self.midiGroup.layout().addWidget(self.inputLabel, 0, 0)
        self.inputCombo = QComboBox(self.midiGroup)
        self.midiGroup.layout().addWidget(self.inputCombo, 0, 1)

        self.outputLabel = QLabel(translate('MIDISettings', 'Output'),
                                  self.midiGroup)
        self.midiGroup.layout().addWidget(self.outputLabel, 1, 0)
        self.outputCombo = QComboBox(self.midiGroup)
        self.midiGroup.layout().addWidget(self.outputCombo, 1, 1)

        self.midiGroup.layout().setColumnStretch(0, 2)
        self.midiGroup.layout().setColumnStretch(1, 3)

        if check_module('Midi'):
            try:
                self._load_devices()
            except Exception:
                self.setEnabled(False)
        else:
            self.setEnabled(False)

    def get_settings(self):
        conf = {}

        if self.isEnabled():
            conf['inputdevice'] = self.inputCombo.currentText()
            MIDIInput().change_port(conf['inputdevice'])
        if self.isEnabled():
            conf['outputdevice'] = self.outputCombo.currentText()
            MIDIOutput().change_port(conf['outputdevice'])

        return {'MIDI': conf}

    def load_settings(self, settings):
        if 'inputdevice' in settings['MIDI']:
            self.inputCombo.setCurrentText('AppDefault')
            self.inputCombo.setCurrentText(settings['MIDI']['inputdevice'])

        if 'outputdevice' in settings['MIDI']:
            self.outputCombo.setCurrentText('AppDefaut')
            self.outputCombo.setCurrentText(settings['MIDI']['outputdevice'])

    def _load_devices(self):
        backend = mido_backend()

        self.inputCombo.clear()
        self.inputCombo.addItems(['AppDefault', 'SysDefault'])
        self.inputCombo.addItems(backend.get_input_names())

        self.outputCombo.clear()
        self.outputCombo.addItems(['AppDefault', 'SysDefault'])
        self.outputCombo.addItems(backend.get_output_names())
