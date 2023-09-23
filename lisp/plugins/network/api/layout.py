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

import json

import falcon

from lisp.cues.cue import CueAction
from lisp.plugins.network.endpoint import EndPoint


class LayoutActionEndPoint(EndPoint):
    UriTemplate = "/layout/action"

    def on_post(self, req, resp):
        try:
            data = json.load(req.stream)
            action = CueAction(data["action"])

            self.app.layout.execute_all(action, quiet=True)
            resp.status = falcon.HTTP_CREATED
        except (KeyError, json.JSONDecodeError):
            resp.status = falcon.HTTP_BAD_REQUEST


class GoEndPoint(EndPoint):
    UriTemplate = "/layout/go"

    def on_post(self, req, resp):
        self.app.layout.go()
        resp.status = falcon.HTTP_CREATED


__endpoints__ = (LayoutActionEndPoint, GoEndPoint)
