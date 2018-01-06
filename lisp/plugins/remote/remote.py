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

from lisp.core.plugin import Plugin
from lisp.plugins.remote.controller import RemoteController
from lisp.plugins.remote.discovery import Announcer


class Remote(Plugin):
    """Provide remote control over cues via RPCs calls."""

    Name = 'Remote'
    Authors = ('Francesco Ceruti', )
    Description = 'Provide remote control of cues over network'

    def __init__(self, app):
        super().__init__(app)

        self._controller = RemoteController(
            app, Remote.Config['IP'], Remote.Config['Port'])
        self._controller.start()

        self._announcer = Announcer(
            Remote.Config['IP'],
            Remote.Config['Discovery']['Port'],
            Remote.Config['Discovery']['Magic']
        )
        self._announcer.start()

    def terminate(self):
        self._controller.stop()
        self._announcer.stop()


def compose_uri(url, port, directory='/'):
    return 'http://' + url + ':' + str(port) + directory