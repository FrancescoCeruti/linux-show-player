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
from .api import API


class API_LayoutAction(API):
    UriTemplate = '/layout/action'

    def on_post(self, req, resp):
        try:
            data = json.load(req.stream)
            action = data['action']

            resp.status = falcon.HTTP_CREATED

            if action == 'GO':
                Application().layout.go()
            elif action == 'STOP_ALL':
                Application().layout.stop_all()
            elif action == 'PAUSE_ALL':
                Application().layout.pause_all()
            elif action == 'RESUME_ALL':
                Application().layout.resume_all()
            else:
                resp.status = falcon.HTTP_BAD_REQUEST

        except(KeyError, json.JSONDecodeError):
            resp.status = falcon.HTTP_BAD_REQUEST


API_EXPORT = (API_LayoutAction, )