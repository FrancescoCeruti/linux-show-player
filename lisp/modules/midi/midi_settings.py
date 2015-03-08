##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QComboBox

from lisp.modules import check_module
from lisp.modules.midi.midi import InputMidiHandler
from lisp.ui.settings.section import SettingsSection


class MIDISettings(SettingsSection):

    NAME = 'MIDI preferences'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # MIDI Input
        self.inputGroup = QGroupBox(self)
        self.inputGroup.setTitle('Input MIDI device')
        self.inputGroup.setLayout(QVBoxLayout())
        self.inputGroup.setGeometry(0, 0, self.width(), 80)

        self.inputCombo = QComboBox(self.inputGroup)
        if check_module('midi'):
            self.inputCombo.addItem('default')
            self.inputCombo.addItems(InputMidiHandler().get_input_names())
        else:
            self.inputCombo.setEnabled(False)
        self.inputGroup.layout().addWidget(self.inputCombo)

    def get_configuration(self):
        conf = {}
        if self.inputCombo.isEnabled():
            conf['inputdevice'] = self.inputCombo.currentText()
            InputMidiHandler().change_port(conf['inputdevice'])

        return {'MIDI': conf}

    def set_configuration(self, conf):
        if 'inputdevice' in conf['MIDI']:
            self.inputCombo.setCurrentText('default')
            # If the device is not found remains 'default'
            self.inputCombo.setCurrentText(conf['MIDI']['inputdevice'])
