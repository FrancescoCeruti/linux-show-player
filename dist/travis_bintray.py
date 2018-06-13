# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2018 Francesco Ceruti <ceppofrancy@gmail.com>
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

import os
import datetime
import json

TEMPLATE = {
    "package": {
        "subject": "francescoceruti",
        "repo": "LinuxShowPlayer",
        "name": "",
        "desc": "Automatic builds from travis-ci",
        "website_url": "https://github.com/FrancescoCeruti/linux-show-player/issues",
        "vcs_url": "https://github.com/FrancescoCeruti/linux-show-player.git",
        "issue_tracker_url": "https://github.com/FrancescoCeruti/linux-show-player/issues",
        "licenses": ["GPL-3.0"],
    },

    "version": {
        "name": "",
        "released": "",
        "desc": ""
    },

    "files": [
    ],

    "publish": True
}

DIR = os.path.dirname(__file__)
TODAY = datetime.datetime.now().strftime('%Y-%m-%d')
DESC_FILE = 'bintray.json'
DESC_PATH = os.path.join(DIR, DESC_FILE)

BRANCH = os.environ['TRAVIS_BRANCH']
COMMIT = os.environ['TRAVIS_COMMIT']
COMMIT_MSG = os.environ['TRAVIS_COMMIT_MESSAGE']
TAG = os.environ.get('TRAVIS_TAG', '')

VERSION = datetime.datetime.now().strftime('%Y.%m.%d_%H:%M')
VERSION += '_{}'.format(TAG if TAG else COMMIT[:7])

print('Creating "{}" ...'.format(DESC_FILE))

# Package
TEMPLATE['package']['name'] = BRANCH
print('>>> Package name:    {}'.format(BRANCH))

# Version
TEMPLATE['version']['name'] = VERSION
print('>>> Version name:    {}'.format(VERSION))

TEMPLATE['version']['released'] = TODAY
print('>>> Version date:    {}'.format(TODAY))

TEMPLATE['version']['desc'] = COMMIT_MSG

if TAG:
    TEMPLATE['version']['vcs_tag'] = TAG

# Files
TEMPLATE['files'].append(
    {
        "includePattern": "dist/Flatpak/out/LinuxShowPlayer.flatpak",
        "uploadPattern": '/{0}/LinuxShowPlayer.flatpak'.format(VERSION),
    }
)

# Save the bintray description
with open(DESC_PATH, mode='w') as out:
    json.dump(TEMPLATE, out, indent=4)

print('{} created.'.format(DESC_FILE))
