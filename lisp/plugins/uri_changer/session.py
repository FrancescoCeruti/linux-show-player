##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import json

from lisp.utils.util import json_deep_search, json_deep_replace


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
