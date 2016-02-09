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

import json

from lisp.modules.uri_changer.json_utils import json_deep_search, \
    json_deep_replace


class Session:

    def __init__(self, file):
        self.file = file
        self.session = {}
        self.prefixes = set()

        self.load()

    def load(self):
        # Read the file content
        with open(self.file, mode='r', encoding='utf-8') as file:
            self.session = json.load(file)

    def analyze(self):
        self.prefixes = set()

        for uri in json_deep_search(self.session, 'uri'):
            prefix = ''

            # The uri should be like "protocol://some/url/here"
            for token in uri[uri.find('://')+4:].split('/')[:-1]:
                prefix += '/' + token
                self.prefixes.add(prefix)

        return self.prefixes

    def replace(self, old, new):
        def replace(value):
            if isinstance(value, str):
                return value.replace(old, new)
            return value

        json_deep_replace(self.session, 'uri', replace)

    def save(self, file):
        with open(file, mode='w', encoding='utf-8') as new_file:
            new_file.write(json.dumps(self.session, sort_keys=True, indent=4))
