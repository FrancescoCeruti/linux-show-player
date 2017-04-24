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

from PyQt5.QtCore import QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton, QMessageBox

from lisp.modules.midi import midi_utils
from lisp.modules.midi.midi_input import MIDIInput
from lisp.ui.settings.settings_page import SettingsPage
from lisp.ui.ui_utils import translate


class ListLayoutControllerSetting(SettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'List Layout Controller')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # midi General Control
        self.setLayout(QVBoxLayout())
        self.midiMapping = QGroupBox()
        self.midiMapping.setTitle(translate('ListLayoutController', 'Midi Mappings'))
        self.midiMapping.setLayout(QVBoxLayout())
        self.layout().addWidget(self.midiMapping)
        self.layout().addStretch()

        self.goMidiButton = QPushButton()
        self.goMidiButton.clicked.connect(self.__learn_midi)
        self.goMidiLabel = QLabel()
        layout = QHBoxLayout()
        layout.addWidget(self.goMidiLabel)
        layout.addWidget(self.goMidiButton)
        self.midiMapping.layout().addLayout(layout)

        self.stopMidiButton = QPushButton()
        self.stopMidiButton.clicked.connect(self.__learn_midi)
        self.stopMidiLabel = QLabel()
        layout = QHBoxLayout()
        layout.addWidget(self.stopMidiLabel)
        layout.addWidget(self.stopMidiButton)
        self.midiMapping.layout().addLayout(layout)

        self.pauseMidiButton = QPushButton()
        self.pauseMidiButton.clicked.connect(self.__learn_midi)
        self.pauseMidiLabel = QLabel()
        layout = QHBoxLayout()
        layout.addWidget(self.pauseMidiLabel)
        layout.addWidget(self.pauseMidiButton)
        self.midiMapping.layout().addLayout(layout)

        self.fadeInMidiButton = QPushButton()
        self.fadeInMidiButton.clicked.connect(self.__learn_midi)
        self.fadeInMidiLabel = QLabel()
        layout = QHBoxLayout()
        layout.addWidget(self.fadeInMidiLabel)
        layout.addWidget(self.fadeInMidiButton)
        self.midiMapping.layout().addLayout(layout)

        self.fadeOutMidiButton = QPushButton()
        self.fadeOutMidiButton.clicked.connect(self.__learn_midi)
        self.fadeOutMidiLabel = QLabel()
        layout = QHBoxLayout()
        layout.addWidget(self.fadeOutMidiLabel)
        layout.addWidget(self.fadeOutMidiButton)
        self.midiMapping.layout().addLayout(layout)

        self.resumeMidiButton = QPushButton()
        self.resumeMidiButton.clicked.connect(self.__learn_midi)
        self.resumeMidiLabel = QLabel()
        layout = QHBoxLayout()
        layout.addWidget(self.resumeMidiLabel)
        layout.addWidget(self.resumeMidiButton)
        self.midiMapping.layout().addLayout(layout)

        self.interruptMidiButton = QPushButton()
        self.interruptMidiButton.clicked.connect(self.__learn_midi)
        self.interruptMidiLabel = QLabel()
        layout = QHBoxLayout()
        layout.addWidget(self.interruptMidiLabel)
        layout.addWidget(self.interruptMidiButton)
        self.midiMapping.layout().addLayout(layout)

        self.retranslateUi()

    def retranslateUi(self):

        self.goMidiLabel.setText(translate('ListLayoutController', 'GO control'))
        self.goMidiButton.setText(translate('ListLayoutController', 'No MIDI mapping'))
        self.stopMidiLabel.setText(translate('ListLayoutController', 'Stop All control'))
        self.stopMidiButton.setText(translate('ListLayoutController', 'No MIDI mapping'))
        self.pauseMidiLabel.setText(translate('ListLayoutController', 'Pause control'))
        self.pauseMidiButton.setText(translate('ListLayoutController', 'No MIDI mapping'))
        self.fadeInMidiLabel.setText(translate('ListLayoutController', 'Fade In control'))
        self.fadeInMidiButton.setText(translate('ListLayoutController', 'No MIDI mapping'))
        self.fadeOutMidiLabel.setText(translate('ListLayoutController', 'Fade Out control'))
        self.fadeOutMidiButton.setText(translate('ListLayoutController', 'No MIDI mapping'))
        self.resumeMidiLabel.setText(translate('ListLayoutController', 'Resume control'))
        self.resumeMidiButton.setText(translate('ListLayoutController', 'No MIDI mapping'))
        self.interruptMidiLabel.setText(translate('ListLayoutController', 'Interrupt control'))
        self.interruptMidiButton.setText(translate('ListLayoutController', 'No MIDI mapping'))

    def get_settings(self):
        conf = {}

        conf['gomidimapping'] = str(self.goMidiButton.text())
        conf['stopmidimapping'] = str(self.stopMidiButton.text())
        conf['pausemidimapping'] = str(self.pauseMidiButton.text())
        conf['fadeinmidimapping'] = str(self.fadeInMidiButton.text())
        conf['fadeoutmidimapping'] = str(self.fadeOutMidiButton.text())
        conf['resumemidimapping'] = str(self.resumeMidiButton.text())
        conf['interruptmidimapping'] = str(self.interruptMidiButton.text())

        return {'ListLayoutController': conf}

    def load_settings(self, settings):
        self.goMidiButton.setText(settings['ListLayoutController']['gomidimapping'])
        self.stopMidiButton.setText(settings['ListLayoutController']['stopmidimapping'])
        self.pauseMidiButton.setText(settings['ListLayoutController']['pausemidimapping'])
        self.fadeInMidiButton.setText(settings['ListLayoutController']['fadeinmidimapping'])
        self.fadeOutMidiButton.setText(settings['ListLayoutController']['fadeoutmidimapping'])
        self.resumeMidiButton.setText(settings['ListLayoutController']['resumemidimapping'])
        self.interruptMidiButton.setText(settings['ListLayoutController']['interruptmidimapping'])

    def __learn_midi(self):
        handler = MIDIInput()
        handler.alternate_mode = True

        def received_message(msg):
            msg_dict = midi_utils.str_msg_to_dict(str(msg))
            try:
                msg_dict.pop('velocity')
            except KeyError:
                pass
            simplified_msg = midi_utils.dict_msg_to_str(msg_dict)
            self.sender().setText(simplified_msg)
            self.midi_learn.accept()

        handler.new_message_alt.connect(received_message)

        self.midi_learn = QMessageBox(self)
        self.midi_learn.setText(translate('ControllerMidiSettings',
                                          'Listening MIDI messages ...'))
        self.midi_learn.setIcon(QMessageBox.Information)
        self.midi_learn.setStandardButtons(QMessageBox.Cancel)

        result = self.midi_learn.exec_()
        if result == QMessageBox.Cancel:
            self.sender().setText(translate('ListLayoutController', 'No MIDI mapping'))

        handler.new_message_alt.disconnect(received_message)
        handler.alternate_mode = False

