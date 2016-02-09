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

from lisp.core.module import Module
from lisp.modules.remote.controller import RemoteController
from lisp.utils.configuration import config


class Remote(Module):
    """Provide remote control over cues via RPCs calls."""

    def __init__(self):
        ip = config['Remote']['BindIp']
        port = int(config['Remote']['BindPort'])

        # Using 'localhost' or similar make the server unreachable from outside
        if ip == 'localhost' or ip.startswith('127.'):
            ip = socket.gethostbyname(socket.gethostname())

        RemoteController(ip=ip, port=port)
        RemoteController().start()

    def terminate(self):
        RemoteController().stop()


def compose_uri(url, port, directory='/'):
    return 'http://' + url + ':' + str(port) + directory