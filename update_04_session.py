#!/usr/bin/env python3
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

import argparse
import json
import os
import sys

parser = argparse.ArgumentParser(
    description='Update LiSP 0.4 sessions to 0.4.1')
parser.add_argument('sessions', nargs='+', help='Session files to be converted')

args = parser.parse_args()

REPLACE = {
    'URIInput': 'UriInput',
    'Equalizer-10bands': 'Equalizer10',
    'Personalized': 'UserElement',
    'PulseAudioSink': 'PulseSink'
}

for session in args.sessions:
    if os.path.exists(session):
        content = {}
        with open(session, mode='r') as sf:
            content.update(json.load(sf))

        for cue in content.get('cues', []):
            pipe = cue.get('_media_', {}).get('pipe', [])
            pipe = [e if e not in REPLACE else REPLACE[e] for e in pipe]
            if pipe:
                cue['_media_']['pipe'] = pipe

            elements = cue.get('_media_', {}).get('elements', {})
            if elements:
                for old_key, new_key in REPLACE.items():
                    if old_key in elements:
                        elements[new_key] = elements.pop(old_key)

        new_session = os.path.splitext(session)[0] + '_041.lsp'
        with open(new_session, mode='w') as sf:
            json.dump(content, sf, sort_keys=True, indent=4)

        print('{} updated'.format(session))
    else:
        print('File not found {}'.format(session), file=sys.stderr)
