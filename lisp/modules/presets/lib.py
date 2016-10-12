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


def preset_path(name):
    """Return the preset-file path.

    :param name: Name of the preset
    :type name: str
    """
    return os.path.join(PRESETS_DIR, name)


def scan_presets(show_error=True):
    """Iterate over presets.

    Every time this function is called a search in `PRESETS_DIR` is performed.

    :param show_error: If True display error to user
    :type show_error: bool
    """
    # TODO: verify if a cached version can improve this function
    try:
        for entry in os.scandir(PRESETS_DIR):
            if entry.is_file():
                yield entry.name
    except OSError as e:
        elogging.exception(translate('Presets', 'Cannot load presets list.'), e,
                           dialog=show_error)


def preset_exists(name):
    """Return True if the preset already exist, False otherwise.

    :param name: Name of the preset
    :type name: str
    :rtype: bool
    """
    return os.path.exists(preset_path(name))


def load_on_cue(preset_name, cue):
    """Load the preset with the given name on cue.

    :param preset_name: The preset to be loaded
    :type preset_name: str
    :param cue: The cue on witch load the preset
    :type cue: lisp.cue.Cue
    """
    cue.update_properties(load_preset(preset_name))


def load_preset(name, show_error=True):
    """Load the preset with the given name and return it.

    :param name: The preset name
    :type name: str
    :param show_error: If True display error to user
    :type show_error: bool
    :rtype: dict
    """
    path = preset_path(name)

    if os.path.exists(path):
        try:
            with open(path, mode='r') as in_file:
                return json.load(in_file)
        except OSError as e:
            elogging.exception(translate('Presets', 'Cannot load preset.'), e,
                               dialog=show_error)

    return {}


def write_preset(name, preset, overwrite=True, show_error=True):
    """Write a preset with the given name in `PRESET_DIR`.

    :param name: The preset name
    :type name: str
    :param preset: The content of the preset
    :type preset: dict
    :param overwrite: If True overwrite existing files
    :type overwrite: bool
    :param show_error: If True display error to user
    :type show_error: bool
    :return: True when no error occurs, False otherwise
    :rtype: bool
    """
    path = preset_path(name)

    if not(not overwrite and os.path.exists(path)):
        try:
            with open(path, mode='w') as out_file:
                json.dump(preset, out_file)

            return True
        except OSError as e:
            elogging.exception(translate('Presets', 'Cannot save presets.'), e,
                               dialog=show_error)

    return False


def rename_preset(old_name, new_name, show_error=True):
    """Rename an exist preset, if the new name is not already used.

    :param old_name: The preset (old) name
    :param new_name: The new preset name
    :param show_error: If True display error to user
    :type show_error: bool
    :return: True if the preset as been renamed successfully, False otherwise
    :rtype: bool
    """
    if preset_exists(old_name) and not preset_exists(new_name):
        try:
            os.rename(preset_path(old_name), preset_path(new_name))
            return True
        except OSError as e:
            elogging.exception(
                translate('Presets', 'Cannot rename presets.'), e,
                dialog=show_error)

    return False


def delete_preset(name):
    """Delete a preset form the file-system.

    :param name: The preset to be deleted
    :type name: str
    :return: True if the preset is deleted, False otherwise
    :rtype: bool
    """
    path = preset_path(name)

    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError as e:
            elogging.exception(
                translate('Presets', 'Cannot delete presets.'), e)
            return False

    # If the path do not exists we return True anyway (just don't tell anyone)
    return True
