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

import mido
from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QHBoxLayout, QLineEdit, \
    QLabel, QGridLayout, QCheckBox, QSpinBox, QPushButton, QComboBox, \
    QMessageBox

from lisp.modules import check_module
from lisp.modules.midi.input_handler import MIDIInputHandler
from lisp.ui.settings.section import SettingsSection


class ControllerSettings(SettingsSection):

    Name = 'MIDI and Hot-Key'

    def __init__(self, size, cue=None, **kwargs):
        super().__init__(size, cue=None, **kwargs)

        self.verticalLayout = QVBoxLayout(self)

        self.keyGroup = QGroupBox(self)
        self.keyGroup.setTitle('Keyboard input')

        self.horizontalLayout = QHBoxLayout(self.keyGroup)

        self.key = QLineEdit(self.keyGroup)
        regex = QRegExp('(.,)*')
        self.key.setValidator(QRegExpValidator(regex))
        self.horizontalLayout.addWidget(self.key)

        self.keyLabel = QLabel('Insert key(s)', self.keyGroup)
        self.keyLabel.setAlignment(Qt.AlignCenter)
        self.horizontalLayout.addWidget(self.keyLabel)

        self.verticalLayout.addWidget(self.keyGroup)

        self.midiGroup = QGroupBox(self)
        self.midiGroup.setTitle('MIDI')

        self.midiLayout = QGridLayout(self.midiGroup)

        self.midiResetCheck = QCheckBox('Reset / Ignore', self.midiGroup)
        self.midiLayout.addWidget(self.midiResetCheck, 0, 0)

        self.midiChannels = QSpinBox(self.midiGroup)
        self.midiChannels.setRange(0, 15)
        self.midiLayout.addWidget(self.midiChannels, 1, 0)
        label = QLabel('Channel', self)
        label.setAlignment(Qt.AlignCenter)
        self.midiLayout.addWidget(label, 1, 1)

        self.midiNote = QSpinBox(self.midiGroup)
        self.midiNote.setRange(0, 255)
        self.midiLayout.addWidget(self.midiNote, 2, 0)
        label = QLabel('Note', self)
        label.setAlignment(Qt.AlignCenter)
        self.midiLayout.addWidget(label, 2, 1)

        self.midiVelocity = QSpinBox(self.midiGroup)
        self.midiVelocity.setRange(0, 255)
        self.midiLayout.addWidget(self.midiVelocity, 3, 0)
        label = QLabel('Velocity', self)
        label.setAlignment(Qt.AlignCenter)
        self.midiLayout.addWidget(label, 3, 1)

        self.midiCapture = QPushButton('Capture', self.midiGroup)
        self.midiCapture.clicked.connect(self.capture_message)
        self.midiLayout.addWidget(self.midiCapture, 4, 0)

        self.noteFilterCombo = QComboBox(self.midiGroup)
        self.midiLayout.addWidget(self.noteFilterCombo, 4, 1)
        self.noteFilterCombo.addItem('Filter "note on"', userData='note_on')
        self.noteFilterCombo.addItem('Filter "note off"', userData='note_off')

        self.verticalLayout.addWidget(self.midiGroup)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 4)

        self.midiResetCheck.toggled.connect(self.on_reset_toggled)

        self.msg_type = 'note_on'

    def enable_check(self, enable):
        self.keyGroup.setCheckable(enable)
        self.keyGroup.setChecked(False)

        self.midiGroup.setCheckable(enable)
        self.midiGroup.setChecked(False)

    def get_configuration(self):
        conf = {}
        checked = self.keyGroup.isCheckable()

        if not (checked and not self.keyGroup.isChecked()):
            # Using a Set to remove duplicates (faster & shorter method)
            conf['hotkeys'] = set(self.key.text().strip().split(','))
            conf['hotkeys'].discard('')
            # But a common type is better for store values
            conf['hotkeys'] = tuple(conf['hotkeys'])

        if not (checked and not self.midiGroup.isChecked()):
            if self.midiResetCheck.isChecked():
                conf['midi'] = ''
            else:
                msg = mido.Message(self.msg_type,
                                   channel=self.midiChannels.value(),
                                   note=self.midiNote.value(),
                                   velocity=self.midiVelocity.value())
                conf['midi'] = str(msg)

        return conf

    def set_configuration(self, conf):
        if 'hotkeys' in conf:
            self.key.setText(','.join(conf['hotkeys']))
        if 'midi' in conf and conf['midi'] != '':
            msg = mido.messages.parse_string(conf['midi'])
            self.msg_type = msg.type
            self.midiChannels.setValue(msg.channel)
            self.midiNote.setValue(msg.note)
            self.midiVelocity.setValue(msg.velocity)
        else:
            self.midiResetCheck.setChecked(True)

        if not check_module('Midi'):
            self.midiGroup.setEnabled(False)

    def capture_message(self):
        handler = MIDIInputHandler()
        handler.alternate_mode = True
        handler.new_message_alt.connect(self.on_new_message)

        QMessageBox.information(self, 'Input',
                                      'Give a MIDI event and press OK')

        handler.new_message_alt.disconnect(self.on_new_message)
        handler.alternate_mode = False

    def on_new_message(self, message):
        t = self.noteFilterCombo.itemData(self.noteFilterCombo.currentIndex())
        if t == message.type:
            self.midiChannels.setValue(message.channel)
            self.midiNote.setValue(message.note)
            self.midiVelocity.setValue(message.velocity)

            self.msg_type = message.type

    def on_reset_toggled(self, checked):
        self.midiChannels.setEnabled(not checked)
        self.midiNote.setEnabled(not checked)
        self.midiVelocity.setEnabled(not checked)
        self.midiCapture.setEnabled(not checked)
        self.noteFilterCombo.setEnabled(not checked)
