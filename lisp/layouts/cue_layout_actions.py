##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from copy import deepcopy

from lisp.core.action import Action
from lisp.cues.cue_factory import CueFactory


class AddAction(Action):

    def __init__(self, layout, cue, index):
        self._layout = layout
        self._cue = cue
        self._index = index

    def do(self):
        if self._cue.is_finalized():
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
        if self._cue.is_finalized():
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
