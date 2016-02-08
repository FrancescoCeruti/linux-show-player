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

import logging
import socket
from http.client import HTTPConnection
from xmlrpc.client import ServerProxy, Fault, Transport
from xmlrpc.server import SimpleXMLRPCServer

from lisp.core.decorators import async
from lisp.core.singleton import Singleton
from lisp.modules.remote.discovery import Announcer
from lisp.modules.remote.dispatcher import RemoteDispatcher


class TimeoutTransport(Transport):
    timeout = 2.0

    def set_timeout(self, timeout):
        self.timeout = timeout

    def make_connection(self, host):
        return HTTPConnection(host, timeout=self.timeout)


class RemoteController(metaclass=Singleton):
    """
        Provide control over a SimpleXMLRPCServer.
    """

    def __init__(self, ip='localhost', port=8070):
        try:
            self.server = SimpleXMLRPCServer((ip, port), allow_none=True,
                                             logRequests=False)
            self._announcer = Announcer()
        except OSError as error:
            # If address already in use
            if error.errno == 98:
                raise Exception(
                    "Only one application instance can use this module")
            else:
                raise error

        self.server.register_introspection_functions()
        self.server.register_instance(RemoteDispatcher())

    @async
    def start(self):
        logging.info('REMOTE: Session started at ' +
                     str(self.server.server_address))

        self._announcer.start()
        self.server.serve_forever()  # Blocking
        self._announcer.stop()

        logging.info('REMOTE: Session ended')

    def stop(self):
        self.server.shutdown()

    @staticmethod
    def connect_to(uri):
        proxy = ServerProxy(uri, transport=TimeoutTransport())

        try:
            # Call a fictive method.
            proxy._()
        except Fault:
            # Connected, the method doesn't exist, which is expected.
            pass
        except socket.error:
            # Not connected, socket error mean that the service is unreachable.
            raise OSError('Session at ' + uri + ' is unreachable')

        # Just in case the method is registered in the XmlRPC server
        return proxy
