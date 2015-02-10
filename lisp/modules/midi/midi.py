##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtCore import pyqtSignal, QObject
import mido

from lisp.core.singleton import QSingleton


# TODO: should be extended for future usage (e.g. multiple ports)
class InputMidiHandler(QObject, metaclass=QSingleton):

    # Only when not in alternate-mode
    new_message = pyqtSignal(mido.messages.BaseMessage)
    # Only when in alternate-mode
    new_message_alt = pyqtSignal(mido.messages.BaseMessage)

    def __init__(self, port_name='default', backend_name=None):
        super().__init__()

        self.alternate_mode = False
        self.backend_name = backend_name
        self.port_name = port_name
        self.backend = None
        self.port = None

    def start(self):
        try:
            self.backend = mido.Backend(self.backend_name, load=True)
        except Exception:
            raise RuntimeError('Backend loading failed: ' + self.backend_name)

        # I'dont expect to find a port named "default", if so, I assume that
        # this port is the default.
        if self.port_name in self.get_input_names():
            self.port = self.backend.open_input(self.port_name,
                                                callback=self._new_message)
        else:
            # If the port isn't available use the default one
            self.port = self.backend.open_input(callback=self._new_message)

    def stop(self):
        if self.port is not None:
            self.port.close()

    def restart(self):
        self.stop()
        self.start()

    def change_port(self, port_name):
        self.port_name = port_name
        self.restart()

    def get_input_names(self):
        if self.backend is not None:
            return self.backend.get_input_names()

        return []

    def get_output_names(self):
        if self.backend is not None:
            return self.backend.get_output_names()

        return []

    def _new_message(self, message):
        if not self.alternate_mode:
            self.new_message.emit(message)
        else:
            self.new_message_alt.emit(message)
