# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

import socket
from threading import Thread

from lisp.core.signal import Signal


class Announcer(Thread):

    def __init__(self, ip, port, magic):
        super().__init__(daemon=True)
        self.magic = magic
        self.address = (ip, port)

        # Create UDP socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        self._socket.bind(self.address)

        self._running = True

    def run(self):
        while self._running:
            data, addr = self._socket.recvfrom(1024)
            if data is not None and addr is not None:
                data = str(data, 'utf-8')
                if data == self.magic:
                    data += socket.gethostname()
                    self._socket.sendto(bytes(data, 'utf-8'), addr)

    def stop(self):
        self._running = False
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        self._socket.close()
        self.join()


class Discoverer(Thread):

    def __init__(self, ip, port, magic):
        super().__init__(daemon=True)
        self.magic = magic
        self.address = (ip, port)

        self.discovered = Signal()

        # Create UDP socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)

        self._running = True
        self._cache = []

    def run(self):
        self._socket.sendto(
            bytes(self.magic, 'utf-8'), self.address
        )

        while self._running:
            data, addr = self._socket.recvfrom(1024)
            if data is not None and addr is not None:
                data = str(data, 'utf-8')
                # Take only the IP, discard the port
                addr = addr[0]
                # Check if valid and new announcement
                if data.startswith(self.magic) and addr not in self._cache:
                    # Get the host name
                    host = data[len(self.magic):]
                    # Append the adders to the cache
                    self._cache.append(addr)
                    # Emit
                    self.discovered.emit((addr, host))

    def stop(self):
        self._running = False
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        self._socket.close()
        self.join()

    def get_discovered(self):
        return self._cache.copy()
