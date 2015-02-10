##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import socket
from threading import Thread

from PyQt5.QtCore import QThread, pyqtSignal
from lisp.utils.configuration import config


PORT = int(config['Remote']['DiscoverPort'])
# To avoid conflicts with other applications
MAGIC = config['Remote']['DiscoverMagic']


class Announcer(Thread):

    def __init__(self):
        super().__init__(daemon=True)
        # Create UDP socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        self._socket.bind(('0.0.0.0', PORT))

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


class Discoverer(QThread):

    discovered = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
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
        self.wait()

    def get_discovered(self):
        return self._cache.copy()
