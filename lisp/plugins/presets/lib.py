# This file is part of Linux Show Player
#
# Copyright 2019 Francesco Ceruti <ceppofrancy@gmail.com>
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
from zipfile import ZipFile

from lisp import app_dirs
from lisp.core.actions_handler import MainActionsHandler
from lisp.cues.cue_actions import UpdateCueAction, UpdateCuesAction

PRESETS_DIR = os.path.join(app_dirs.user_data_dir, "presets")


def preset_path(name):
    """Return the preset-file path.

    :param name: Name of the preset
    :type name: str
    """
    return os.path.join(PRESETS_DIR, name)


def scan_presets():
    """Iterate over presets.

    Every time this function is called a search in `PRESETS_DIR` is performed.
    """
    for entry in os.scandir(PRESETS_DIR):
        if entry.is_file():
            yield entry.name


def preset_exists(name):
    """Return True if the preset already exist, False otherwise.

    :param name: Name of the preset
    :type name: str
    :rtype: bool
    """
    return os.path.exists(preset_path(name))


def load_on_cue(preset_name, cue):
    """Load the preset with the given name on cue.

    Use `UpdateCueAction`

    :param preset_name: The preset to be loaded
    :type preset_name: str
    :param cue: The cue on which load the preset
    :type cue: lisp.cue.Cue
    """
    MainActionsHandler.do_action(UpdateCueAction(load_preset(preset_name), cue))


def load_on_cues(preset_name, cues):
    """
    Use `UpdateCuesAction`

    :param preset_name: The preset to be loaded
    :type preset_name: str
    :param cues: The cues on which load the preset
    :type cues: typing.Iterable[lisp.cue.Cue]
    """
    MainActionsHandler.do_action(
        UpdateCuesAction(load_preset(preset_name), cues)
    )


def load_preset(name):
    """Load the preset with the given name and return it.

    :param name: The preset name
    :type name: str
    :rtype: dict
    """
    path = preset_path(name)

    with open(path, mode="r") as in_file:
        return json.load(in_file)


def write_preset(name, preset):
    """Write a preset with the given name in `PRESET_DIR`.

    :param name: The preset name
    :type name: str
    :param preset: The content of the preset
    :type preset: dict
    :return: True when no error occurs, False otherwise
    :rtype: bool
    """
    path = preset_path(name)

    with open(path, mode="w") as out_file:
        json.dump(preset, out_file)


def rename_preset(old_name, new_name):
    """Rename an existing preset, if the new name is not already used.

    :param old_name: The preset (old) name
    :param new_name: The new preset name
    :return: True if the preset as been renamed successfully, False otherwise
    :rtype: bool
    """
    os.rename(preset_path(old_name), preset_path(new_name))


def delete_preset(name):
    """Delete a preset form the file-system.

    :param name: The preset to be deleted
    :type name: str
    """
    path = preset_path(name)

    if os.path.exists(path):
        os.remove(path)


def export_presets(names, archive):
    """Export presets-files into an archive.

    :param names: The presets to be exported
    :type names: typing.Iterable[Str]
    :param archive: The path of the archive
    :type archive: str
    """
    if names:
        with ZipFile(archive, mode="w") as archive:
            for name in names:
                archive.write(preset_path(name), name)


def import_presets(archive, overwrite=True):
    """Import presets for an archive.

    :param archive: The archive path
    :type archive: str
    :param overwrite: Overwrite existing files
    :type overwrite: bool
    """
    with ZipFile(archive) as archive:
        for member in archive.namelist():
            if not (preset_exists(member) and not overwrite):
                archive.extract(member, path=PRESETS_DIR)


def import_has_conflicts(archive):
    """Verify if the `archive` files conflicts with the user presets.

    :param archive: path of the archive to analyze
    :type archive: str
    :rtype: bool
    """
    with ZipFile(archive) as archive:
        for member in archive.namelist():
            if preset_exists(member):
                return True

    return False


def import_conflicts(archive):
    """Return a list of conflicts between `archive` files and user presets.

    :param archive: path of the archive to analyze
    :type archive: str
    """
    conflicts = []

    with ZipFile(archive) as archive:
        for member in archive.namelist():
            if preset_exists(member):
                conflicts.append(member)

    return conflicts
