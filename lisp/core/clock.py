##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from threading import Lock

from PyQt5.QtCore import QTimer

from lisp.core.singleton import QSingleton
from lisp.utils.decorators import synchronized


class Clock(QTimer, metaclass=QSingleton):
    '''
        Clock based on Qt.QTimer class.

        The class provide two functions for add and remove
        callback, in this way the clock is running only when
        there's one, or more, callback.
    '''

    def __init__(self, timeout=100):
        super().__init__()
        self.setInterval(timeout)

        self.__clients = 0


    @synchronized
    def add_callback(self, callback):
        self.timeout.connect(callback)

        self.__clients += 1
        if self.__clients == 1:
            self.start()

    @synchronized
    def remove_callback(self, callback):
        self.timeout.disconnect(callback)

        self.__clients -= 1
        if self.__clients == 0:
            self.stop()
