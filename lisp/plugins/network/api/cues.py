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


def resolve_cue(app, cue_id):
    cue = app.cue_model.get(cue_id)

    if cue is None:
        raise falcon.HTTPNotFound()

    return cue


class CuesListEndPoint(EndPoint):
    UriTemplate = "/cues"

    def on_get(self, request, response):
        response.status = falcon.HTTP_OK
        response.body = json.dumps({"cues": tuple(self.app.cue_model.keys())})


class CueEndPoint(EndPoint):
    UriTemplate = "/cues/{cue_id}"

    def on_get(self, request, response, cue_id):
        cue = resolve_cue(self.app, cue_id)

        response.status = falcon.HTTP_OK
        response.body = json.dumps(cue.properties())


class CueActionEndPoint(EndPoint):
    UriTemplate = "/cues/{cue_id}/action"

    def on_post(self, request, response, cue_id):
        cue = resolve_cue(self.app, cue_id)

        try:
            data = json.load(request.stream)
            action = CueAction(data["action"])

            cue.execute(action=action)
            response.status = falcon.HTTP_CREATED
        except (KeyError, json.JSONDecodeError):
            response.status = falcon.HTTP_BAD_REQUEST


class CueStateEndPoint(EndPoint):
    UriTemplate = "/cues/{cue_id}/state"

    def on_get(self, request, response, cue_id):
        cue = resolve_cue(self.app, cue_id)

        response.status = falcon.HTTP_OK
        response.body = json.dumps(
            {
                "state": cue.state,
                "current_time": cue.current_time(),
                "prewait_time": cue.prewait_time(),
                "postwait_time": cue.postwait_time(),
            }
        )


__endpoints__ = (
    CueEndPoint,
    CueActionEndPoint,
    CuesListEndPoint,
    CueStateEndPoint,
)
