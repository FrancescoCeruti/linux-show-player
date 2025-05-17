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

from lisp.cues.cue import CueAction
from lisp.plugins.network.endpoint import EndPoint


class LayoutActionEndPoint(EndPoint):
    UriTemplate = "/layout/action"

    def on_post(self, request, response):
        try:
            data = request.get_media()
            action = CueAction(data.get("action"))

            self.app.layout.execute_all(action, quiet=True)
            response.status = falcon.HTTP_CREATED
        except ValueError:
            response.status = falcon.HTTP_BAD_REQUEST


class GoEndPoint(EndPoint):
    UriTemplate = "/layout/go"

    def on_post(self, request, response):
        self.app.layout.go()
        response.status = falcon.HTTP_CREATED


__endpoints__ = (LayoutActionEndPoint, GoEndPoint)
