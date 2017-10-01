# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2017 Francesco Ceruti <ceppofrancy@gmail.com>
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
from wsgiref.simple_server import make_server

import falcon

from lisp.core.decorators import async
from lisp.core.module import Module
from .api import load_api


class Remote(Module):
    def __init__(self):
        self.server = None
        self.app = falcon.API()
        # for development environment
        self.app.resp_options.secure_cookies_by_default = False

        load_api(self.app)

        self.start()

    @async
    def start(self):
        with make_server('', 9090, self.app) as self.server:
            logging.info('REMOTE2: Server started at {}'.format(
                self.server.server_address))

            self.server.serve_forever()

            logging.info('REMOTE2: Server stopped')

    def terminate(self):
        if self.server is not None:
            self.server.server_close()
