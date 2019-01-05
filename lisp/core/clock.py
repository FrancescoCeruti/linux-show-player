# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from threading import Lock

from PyQt5.QtCore import QTimer


class Clock(QTimer):
    """Clock based on Qt.QTimer class.

    The class provide two functions to add and remove
    callbacks, in this way the clock is running only when
    there's one, or more, callbacks.
    """

    def __init__(self, timeout):
        super().__init__()
        self.setInterval(timeout)

        self.__lock = Lock()
        self.__clients = 0

    def add_callback(self, callback):
        with self.__lock:
            self.timeout.connect(callback)

            self.__clients += 1
            if self.__clients == 1:
                self.start()

    def remove_callback(self, callback):
        with self.__lock:
            self.timeout.disconnect(callback)

            self.__clients -= 1
            if self.__clients == 0:
                self.stop()


Clock_10 = Clock(10)
Clock_100 = Clock(100)
