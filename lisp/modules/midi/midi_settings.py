##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QComboBox, QMessageBox

from lisp.modules import check_module
from lisp.modules.midi.midi import InputMidiHandler
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
            InputMidiHandler().change_port(conf['inputdevice'])

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
            self.deviceCombo.addItems(InputMidiHandler().get_input_names())
        else:
            self.deviceCombo.setEnabled(False)

    def _change_backend(self, current):
        self.setEnabled(False)
        try:
            InputMidiHandler().change_backend(self.BACKENDS[current])
            self._load_devices()
        except RuntimeError as e:
            QMessageBox.critical(self, 'Error', str(e))
        finally:
            self.setEnabled(True)
