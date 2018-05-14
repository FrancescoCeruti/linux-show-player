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

import json

import falcon

from lisp.application import Application
from lisp.cues.cue import CueAction
from .api import API


def resolve_cue(req, resp, resource, params):
    cue_id = params.pop('cue_id', None)
    cue = Application().cue_model.get(cue_id)

    if cue is None:
        raise falcon.HTTPNotFound()

    params['cue'] = cue


class API_CuesList(API):
    UriTemplate = '/cues'

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_OK
        resp.body = json.dumps({
            'cues': tuple(Application().cue_model.keys())
        })


@falcon.before(resolve_cue)
class API_Cue(API):
    UriTemplate = '/cues/{cue_id}'

    def on_get(self, req, resp, cue):
        resp.status = falcon.HTTP_OK
        resp.body = json.dumps(cue.properties())


@falcon.before(resolve_cue)
class API_CueAction(API):
    UriTemplate = '/cues/{cue_id}/action'

    def on_post(self, req, resp, cue):
        try:
            data = json.load(req.stream)
            action = CueAction(data['action'])

            cue.execute(action=action)
            resp.status = falcon.HTTP_CREATED
        except(KeyError, json.JSONDecodeError):
            resp.status = falcon.HTTP_BAD_REQUEST


@falcon.before(resolve_cue)
class API_CueState(API):
    UriTemplate = '/cues/{cue_id}/state'

    def on_get(self, req, resp, cue):
        resp.status = falcon.HTTP_OK
        resp.body = json.dumps({
            'state': cue.state,
            'current_time': cue.current_time(),
            'prewait_time': cue.prewait_time(),
            'postwait_time': cue.postwait_time()
        })

API_EXPORT = (API_Cue, API_CueAction, API_CuesList, API_CueState)
