# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2018 Francesco Ceruti <ceppofrancy@gmail.com>
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
from lisp.plugins.remote.dispatcher import RemoteDispatcher

logger = logging.getLogger(__name__)


class TimeoutTransport(Transport):
    timeout = 2.0

    def set_timeout(self, timeout):
        self.timeout = timeout

    def make_connection(self, host):
        return HTTPConnection(host, timeout=self.timeout)


class RemoteController:
    """Provide control over a SimpleXMLRPCServer."""

    def __init__(self, app, ip, port):
        self.server = SimpleXMLRPCServer(
            (ip, port), allow_none=True, logRequests=False)

        self.server.register_introspection_functions()
        self.server.register_instance(RemoteDispatcher(app))

    @async
    def start(self):
        logger.info(
            'Remote network session started: IP="{}" Port="{}"'.format(
                self.server.server_address[0],
                self.server.server_address[1]
            )
        )

        # Blocking call
        self.server.serve_forever()

        logger.info('Remote network session ended.')

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

        return proxy
