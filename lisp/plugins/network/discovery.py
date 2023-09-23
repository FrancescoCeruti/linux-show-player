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

import socket
import socketserver
from threading import Thread

from lisp.core.signal import Signal


class Announcer(Thread):
    """Allow other hosts on a network to discover a specific "service" via UDP.

    While this class is called "Announcer" it acts passively, only responding
    to requests, it does not advertise itself on the network.
    """

    def __init__(self, ip, port, magic):
        super().__init__(daemon=True)
        self.server = socketserver.UDPServer((ip, port), AnnouncerUDPHandler)
        self.server.bytes_magic = bytes(magic, "utf-8")

    def run(self):
        with self.server:
            self.server.serve_forever()

    def stop(self):
        if self.is_alive():
            self.server.shutdown()
            self.join()


class AnnouncerUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]

        if data == self.server.bytes_magic:
            socket.sendto(data, self.client_address)


class Discoverer(Thread):
    """Actively search for an announced "service" on a network.

    By default, does only a few attempts to find active (announced)
    host on the network.
    """

    def __init__(
        self, port, magic, max_attempts=3, timeout=0.5, target="<broadcast>"
    ):
        super().__init__(daemon=True)

        self.address = (target, port)
        self.bytes_magic = bytes(magic, "utf-8")
        self.max_attempts = max_attempts
        self.timeout = timeout

        # Emitted when a new host has been discovered (ip, fully-qualified-name)
        self.discovered = Signal()
        # Emitted on discovery ended
        self.ended = Signal()

        self._stop_flag = False
        self._cache = set()

    def _new_socket(self):
        """Return a new broadcast UDP socket"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        s.settimeout(self.timeout)

        return s

    def _send_beacon(self, socket):
        socket.sendto(self.bytes_magic, self.address)

    def run(self):
        self._stop_flag = False

        with self._new_socket() as sock:
            self._send_beacon(sock)
            attempts = 1

            while not self._stop_flag:
                try:
                    data, address = sock.recvfrom(1024)
                    host = address[0]
                    # Check if the response is valid and if the host
                    # has already replied
                    if data == self.bytes_magic and host not in self._cache:
                        fqdn = socket.getfqdn(host)
                        self._cache.add(host)
                        self.discovered.emit(host, fqdn)
                except OSError:
                    if attempts >= self.max_attempts:
                        break

                    attempts += 1
                    self._send_beacon(sock)

        self.ended.emit()

    def stop(self):
        self._stop_flag = True
        self.join()

    def get_discovered(self):
        return list(self._cache)
