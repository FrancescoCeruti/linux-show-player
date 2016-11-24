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

from lisp.core.configuration import config
from lisp.core.signal import Signal

IP = config['Remote']['BindIp']
PORT = int(config['Remote']['DiscoverPort'])
# To avoid conflicts with other applications
MAGIC = config['Remote']['DiscoverMagic']


class Announcer(Thread):

    def __init__(self):
        super().__init__(daemon=True)
        # Create UDP socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        self._socket.bind((IP, PORT))

        self._running = True

    def run(self):
        while self._running:
            data, addr = self._socket.recvfrom(1024)
            if data is not None and addr is not None:
                data = str(data, 'utf-8')
                if data == MAGIC:
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

    def __init__(self):
        super().__init__()
        self.discovered = Signal()

        # Create UDP socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)

        self._running = True
        self._cache = []

    def run(self):
        self._socket.sendto(bytes(MAGIC, 'utf-8'), ('<broadcast>', PORT))

        while self._running:
            data, addr = self._socket.recvfrom(1024)
            if data is not None and addr is not None:
                data = str(data, 'utf-8')
                # Take only the IP, discard the port
                addr = addr[0]
                # Check if valid and new announcement
                if data.startswith(MAGIC) and addr not in self._cache:
                    # Get the host name
                    host = data[len(MAGIC):]
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
