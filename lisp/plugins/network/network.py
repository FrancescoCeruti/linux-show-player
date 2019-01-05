# This file is part of Linux Show Player
#
# Copyright 2017 Francesco Ceruti <ceppofrancy@gmail.com>
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

import falcon

from lisp.core.plugin import Plugin
from lisp.plugins.network.api import route_all
from lisp.plugins.network.server import APIServerThread
from lisp.plugins.network.discovery import Announcer


class Network(Plugin):
    Name = "Network"
    Description = "Allow the application to be controlled via network."
    Authors = ("Francesco Ceruti",)

    def __init__(self, app):
        super().__init__(app)
        self.api = falcon.API()
        # We don't support HTTPS (yet?)
        self.api.resp_options.secure_cookies_by_default = False
        # Load all the api endpoints
        route_all(self.app, self.api)

        # WSGI Server
        self.server = APIServerThread(
            Network.Config["host"], Network.Config["port"], self.api
        )
        self.server.start()

        # Announcer
        self.announcer = Announcer(
            Network.Config["host"],
            Network.Config["discovery.port"],
            Network.Config["discovery.magic"],
        )
        self.announcer.start()

    def terminate(self):
        self.announcer.stop()
        self.server.stop()
