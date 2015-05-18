# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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

from copy import deepcopy

from lisp.core.action import Action
from lisp.cues.cue_factory import CueFactory


class AddAction(Action):

    def __init__(self, layout, cue, index):
        self._layout = layout
        self._cue = cue
        self._index = index

    def do(self):
        if self._cue.finalized():
            self._cue = CueFactory.clone_cue(self._cue, same_id=True)

        self._layout.__add_cue__(self._cue, self._index)

    def undo(self):
        self._layout.__remove_cue__(self._cue)

    def redo(self):
        self.do()

    def log(self):
        return 'Cue added'


class RemoveAction(Action):

    def __init__(self, layout, cue, index):
        self._layout = layout
        self._cue = cue
        self._index = index

    def do(self):
        self._layout.__remove_cue__(self._cue)

    def undo(self):
        if self._cue.finalized():
            self._cue = CueFactory.clone_cue(self._cue, same_id=True)

        self._layout.__add_cue__(self._cue, self._index)

    def redo(self):
        self.do()

    def log(self):
        return 'Cue removed'


class ConfigureAction(Action):

    def __init__(self, properties, cue):
        self._cue = cue
        self._new = properties
        self._old = deepcopy(cue.properties())

    def do(self):
        self._cue.update_properties(deepcopy(self._new))

    def undo(self):
        self._cue.update_properties(deepcopy(self._old))

    def redo(self):
        self.do()

    def log(self):
        return 'Cue configuration changed'


class MultiConfigureAction(Action):

    def __init__(self, properties, cues):
        self._cues = cues
        self._new = properties
        self._old = [deepcopy(cue.properties()) for cue in cues]

    def do(self):
        for cue in self._cues:
            cue.update_properties(deepcopy(self._new))

    def undo(self):
        for cue, old in zip(self._cues, self._old):
            cue.update_properties(deepcopy(old))

    def redo(self):
        self.do()

    def log(self):
        return 'Cues configuration changed'


class MoveAction(Action):

    def __init__(self, layout, cue, to_index):
        self._cue = cue
        self._layout = layout
        self._to_index = to_index
        self._from_index = cue['index']

    def do(self):
        self._layout.__move_cue__(self._cue, self._to_index)

    def undo(self):
        self._layout.__move_cue__(self._cue, self._from_index)

    def redo(self):
        self.do()

    def log(self):
        return 'Cue moved'
