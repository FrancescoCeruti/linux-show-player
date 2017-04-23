# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2016-2017 Aurélien Cibrario <aurelien.cibrario@gmail.com>
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

from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

from lisp.modules.midi.midi_input import MIDIInput
from lisp.ui.settings.settings_page import SettingsPage
from lisp.ui.ui_utils import translate


class ListLayoutControllerSetting(QGroupBox, SettingsPage):
    Name = 'List Layout Controller'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # midi General Control
        self.setLayout(QHBoxLayout())

        self.goMidiButton = QPushButton()
        self.goMidiButton.clicked.connect(self.on_go_midi_clicked)
        self.goMidiLabel = QLabel()
        self.layout().addWidget(self.goMidiLabel)
        self.layout().addWidget(self.goMidiButton)

        self.retranslateUi()

    def retranslateUi(self):
        self.setTitle(translate('ListLayout', 'General Midi Control'))
        self.goMidiLabel.setText(translate('ListLayout', 'GO control'))
        self.goMidiButton.setText(translate('ListLayout', 'No midi mapping'))

    def get_settings(self):

        settings = {
            'gomidimapping': str(self.goMidiButton.text()),
        }

        for key, val in settings.items():
            yield (key, val)

    def load_settings(self, settings):
        self.goMidiButton.setText(settings.get('gomidimapping'))

    def on_go_midi_clicked(self):
        handler = MIDIInput()
        handler.alternate_mode = True
        handler.new_message_alt.connect(self.__received_message)

        self.midi_learn = QMessageBox(self)
        self.midi_learn.setText(translate('ControllerMidiSettings',
                                          'Listening MIDI messages ...'))
        self.midi_learn.setIcon(QMessageBox.Information)
        self.midi_learn.setStandardButtons(QMessageBox.Cancel)
        result = self.midi_learn.exec_()
        if result == QMessageBox.Cancel:
            self.goMidiButton.setText(translate('ListLayout', 'No midi mapping'))

        handler.new_message_alt.disconnect(self.__received_message)

    def __received_message(self, msg):
        self.goMidiButton.setText(str(msg))
        self.midi_learn.accept()


