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

from lisp.core.action import Action


class RenameCueAction(Action):

    # Store names for undo/redo in a dict like that : {'id': name}
    names = {}

    def __init__(self, app, new_cue_list):
        """Store new names with id"""
        self.app = app

        for renamed_cue in new_cue_list:
            self.names[renamed_cue["id"]] = renamed_cue["cue_preview"]

    def do(self):
        """Use stored name and exchange with current names"""
        for id in self.names:
            cue = self.app.cue_model.get(id)
            cue.name, self.names[id] = self.names[id], cue.name

    def undo(self):
        """Restore previous names and save current for redo"""
        self.do()
