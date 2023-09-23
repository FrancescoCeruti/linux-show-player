# This file is part of Linux Show Player
#
# Copyright 2016-2017 Aurelien Cibrario <aurelien.cibrario@gmail.com>
# Copyright 2017 Francesco Ceruti <ceppofrancy@gmail.com>
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

from lisp.command.command import Command
from lisp.ui.ui_utils import translate


class RenameCuesCommand(Command):
    __slots__ = ("_model", "_names")

    def __init__(self, model, rename_list):
        self._model = model
        self._names = {}

        for renamed_cue in rename_list:
            self._names[renamed_cue["id"]] = renamed_cue["cue_preview"]

    def do(self):
        """Use stored name and exchange with current names"""
        for id in self._names:
            cue = self._model.get(id)
            cue.name, self._names[id] = self._names[id], cue.name

    def undo(self):
        """Restore previous names and save current for redo"""
        self.do()

    def log(self) -> str:
        return translate("RenameCuesCommand", "Renamed {number} cues").format(
            number=len(self._names)
        )
