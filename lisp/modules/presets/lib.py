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
import os

from lisp.ui.ui_utils import translate
from lisp.utils import configuration
from lisp.utils import elogging

PRESETS_DIR = os.path.join(configuration.CFG_DIR, 'presets')


def scan_presets():
    """Iterate over presets.

    Every time this function is called a search in `PRESETS_DIR` is performed.
    """
    # TODO: verify if a cached version can improve this function
    try:
        for entry in os.scandir(PRESETS_DIR):
            if entry.is_file():
                yield entry.name
    except OSError as e:
        elogging.exception(
            translate('Presets', 'Error while reading presets.'), e)


def preset_exists(name):
    """Return True if the preset already exist, False otherwise.

    :param name: Name of the preset
    :rtype: bool
    """
    return os.path.exists(os.path.join(PRESETS_DIR, name))


def load_on_cue(preset_name, cue):
    """Load the preset with the given name on cue.

    :param preset_name: The preset to be loaded
    :type preset_name: str
    :param cue: The cue on witch load the preset
    :type cue: lisp.cue.Cue
    """
    cue.update_properties(load_preset(preset_name))


def load_preset(name, noerror=True):
    """Load the preset with the given name and return it.

    :param name: The preset name
    :type name: str
    :param noerror: If True no exception is raised if the preset do not exists
    :type noerror: bool
    :rtype: dict

    :raise FileNotFoundError: if the preset doesn't exists and noerror is False
    """
    path = os.path.join(PRESETS_DIR, name)

    if os.path.exists(path):
        with open(path, mode='r') as in_file:
            return json.load(in_file)
    elif not noerror:
        raise FileNotFoundError('The preset-file do not exits: {}'.format(path))

    return {}


def write_preset(name, preset, overwrite=True):
    """Write a preset with the given name in `PRESET_DIR`.

    :param name: The preset name
    :type name: str
    :param preset: The content of the preset
    :type preset: dict
    :param overwrite: If True overwrite existing files
    :type overwrite: bool

    :raise FileExistsError: if `overwrite` is False an the preset-file exists
    """
    path = os.path.join(PRESETS_DIR, name)

    if not overwrite and os.path.exists(path):
        raise FileExistsError('The preset-file already exist: {}'.format(path))

    with open(path, mode='w') as out_file:
        json.dump(preset, out_file)


def delete_preset(name):
    """Delete a preset form the file-system.

    :param name: The preset to be deleted
    :type name: str
    """
    path = os.path.join(PRESETS_DIR, name)

    if os.path.exists(path):
        os.remove(path)