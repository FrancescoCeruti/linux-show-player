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
        self.__backend_name = backend_name
        self.__port_name = port_name
        self.__backend = None
        self.__port = None

    def start(self):
        if self.__backend is None:
            try:
                self.__backend = mido.Backend(self.__backend_name, load=True)
                self.__open_port()
            except Exception:
                raise RuntimeError('Backend loading failed: ' +
                                   self.__backend_name)

    def stop(self):
        self.__close_port()
        self.__backend = None

    def change_backend(self, backand_name):
        self.stop()
        self.__backend_name = backand_name
        self.start()

    def change_port(self, port_name):
        self.__port_name = port_name
        self.__close_port()
        self.__open_port()

    def get_input_names(self):
        if self.__backend is not None:
            return self.__backend.get_input_names()

        return []

    def _new_message(self, message):
        if not self.alternate_mode:
            self.new_message.emit(message)
        else:
            self.new_message_alt.emit(message)

    def __open_port(self):
        # I'dont expect to find a __port named "default", if so, I assume
        # this __port is the default one.
        if self.__port_name in self.get_input_names():
            self.__port = self.__backend.open_input(self.__port_name,
                                                    callback=self._new_message)
        else:
            # If the __port isn't available use the default one
            self.__port = self.__backend.open_input(callback=self._new_message)

    def __close_port(self):
        if self.__port is not None:
            self.__port.close()
