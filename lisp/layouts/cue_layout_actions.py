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

from copy import deepcopy

from lisp.core.action import Action
from lisp.utils.util import dict_diff


class ConfigureAction(Action):

    __slots__ = ('__cue', '__new', '__old')

    def __init__(self, properties, cue):
        self.__cue = cue

        cue_properties = deepcopy(cue.properties())
        self.__new = dict(dict_diff(cue_properties, properties))
        self.__old = dict(dict_diff(properties, cue_properties))

    def do(self):
        self.__cue.update_properties(deepcopy(self.__new))

    def undo(self):
        self.__cue.update_properties(deepcopy(self.__old))

    def redo(self):
        self.do()

    def log(self):
        return 'Cue configuration changed'


class MultiConfigureAction(Action):

    __slots__ = ('__cues', '__new', '__old')

    def __init__(self, properties, cues):
        self.__cues = cues
        self.__new = []
        self.__old = []

        for cue in cues:
            cue_properties = deepcopy(cue.properties())
            self.__new.append(dict(dict_diff(cue_properties, properties)))
            self.__old.append(dict(dict_diff(properties, cue_properties)))

    def do(self):
        for cue, new in zip(self.__cues, self.__new):
            cue.update_properties(deepcopy(new))

    def undo(self):
        for cue, old in zip(self.__cues, self.__old):
            cue.update_properties(deepcopy(old))

    def redo(self):
        self.do()

    def log(self):
        return 'Cues configuration changed'
