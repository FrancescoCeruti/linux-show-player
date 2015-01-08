##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtCore import pyqtSignal, QObject
from lisp.utils.configuration import config
import mido

from lisp.ui.settings.app_settings import AppSettings
from lisp.core.singleton import QSingleton

from .midi_settings import MIDISettings


def initialize():
    # Register the settings widget
    AppSettings.register_settings_widget(MIDISettings)

    # Start the MIDI-event Handler
    port_name = config['MIDI']['InputDevice']
    backend = config['MIDI']['Backend']

    InputMidiHandler(port_name=port_name, backend=backend)
    InputMidiHandler().start()


def terminate():
    # Stop the MIDI-event Handler
    InputMidiHandler().stop()

    # Unregister the settings widget
    AppSettings.unregister_settings_widget(MIDISettings)


def get_input_names():
    return mido.get_input_names()


def get_output_names():
    return mido.get_output_names()


# NOTE: Currently only "note_on" and "note_off" are handled
# TODO: should be extended for future usage (e.g. multiple ports)
class InputMidiHandler(QObject, metaclass=QSingleton):

    # Only when not in alternate-mode
    new_message = pyqtSignal(mido.messages.BaseMessage)
    # Only when in alternate-mode
    new_message_alt = pyqtSignal(mido.messages.BaseMessage)

    def __init__(self, port_name='default', backend=None):
        super().__init__()

        self.alternate_mode = False
        self.port_name = port_name
        self.backend = backend
        self.port = None
        self.device = None

    def restart(self):
        self.stop()
        self.start()

    def change_device(self, device):
        self.device = device
        self.restart()

    def start(self):
        try:
            mido.set_backend(self.backend)

            if self.port_name != 'default':
                self.port = mido.open_input(self.port_name, callback=self._new_message)
            else:
                self.port = mido.open_input(callback=self._new_message)
        except Exception:
            raise RuntimeError('Backend loading failed: ' + self.backend)

    def stop(self):
        if self.port is not None:
            self.port.close()

    def _new_message(self, message):
        if message.type in ['note_on', 'note_off']:
            if not self.alternate_mode:
                self.new_message.emit(message)
            else:
                self.new_message_alt.emit(message)
