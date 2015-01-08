##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtWidgets import *  # @UnusedWildImport
import mido

from lisp.modules import check_module
from lisp.ui.settings.section import SettingsSection


class MIDISettings(SettingsSection):

    NAME = 'MIDI preferences'

    Backends = {'RtMidi': 'mido.backends.rtmidi',
                'PortMidi': 'mido.backends.portmidi'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # MIDI Input
        self.inputGroup = QGroupBox(self)
        self.inputGroup.setTitle('Input MIDI device')
        self.inputGroup.setLayout(QVBoxLayout())
        self.inputGroup.setGeometry(0, 0, self.width(), 80)

        self.inputCombo = QComboBox(self.inputGroup)
        if check_module('midi'):
            self.inputCombo.addItems(mido.get_input_names() + ['default'])
        else:
            self.inputCombo.setEnabled(False)
        self.inputGroup.layout().addWidget(self.inputCombo)

        # MIDI Backend
        self.backendGroup = QGroupBox(self)
        self.backendGroup.setTitle('MIDI backend')
        self.backendGroup.setLayout(QVBoxLayout())
        self.backendGroup.setGeometry(0, 85, self.width(), 80)

        self.backendCombo = QComboBox(self.backendGroup)
        self.backendCombo.addItems(self.Backends.keys())
        self.backendGroup.layout().addWidget(self.backendCombo)

    def get_configuration(self):
        conf = {}
        if self.inputCombo.isEnabled():
            conf['inputdevice'] = self.inputCombo.currentText()
        conf['backend'] = self.Backends[self.backendCombo.currentText()]
        return {'MIDI': conf}

    def set_configuration(self, conf):
        if 'inputdevice' in conf['MIDI']:
            self.inputCombo.setCurrentText('default')
            # If the device is not found remains 'default'
            self.inputCombo.setCurrentText(conf['MIDI']['inputdevice'])
        if 'backend' in conf['MIDI']:
            for name, bk in self.Backends.items():
                if conf['MIDI']['backend'] == bk:
                    self.backendCombo.setCurrentText(name)
                    break
