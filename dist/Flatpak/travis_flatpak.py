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
import json

DIR = os.path.dirname(__file__)
APP_ID = "com.github.FrancescoCeruti.LinuxShowPlayer"
MANIFEST = os.path.join(DIR, APP_ID + '.json')
BRANCH = os.environ['TRAVIS_BRANCH']
COMMIT = os.environ['TRAVIS_COMMIT']

LiSP_MODULE = 'linux-show-player'

# Load the manifest (as dictionary)
with open(MANIFEST, mode='r') as template:
    manifest = json.load(template)

# Patch top-Level attributes
manifest['branch'] = BRANCH
if BRANCH != 'master':
    manifest['desktop-file-name-suffix'] = ' ({})'.format(BRANCH)

# Patch modules attributes
source = {}
for module in reversed(manifest['modules']):
    if module['name'] == LiSP_MODULE:
        source = module['sources'][0]
        break

source['branch'] = BRANCH
source['commit'] = COMMIT

# Save the patched manifest
with open(MANIFEST, mode='w') as out:
    json.dump(manifest, out, indent=4)
