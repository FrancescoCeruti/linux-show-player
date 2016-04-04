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

from ast import literal_eval

from lisp.core.action import Action


class CueUpdateAction(Action):

    __slots__ = ('__cue', '__new', '__old')

    def __init__(self, properties, cue):
        self.__cue = cue

        self.__new = properties
        self.__old = str(cue.properties())

    def do(self):
        self.__cue.update_properties(self.__new)
        self.__new = str(self.__new)

    def undo(self):
        self.__cue.update_properties(literal_eval(self.__old))

    def redo(self):
        self.__new = literal_eval(self.__new)
        self.do()

    def log(self):
        return 'Cue configuration changed'


class CuesUpdateAction(Action):

    __slots__ = ('__cues', '__new', '__old')

    def __init__(self, properties, cues):
        self.__cues = cues
        self.__new = properties
        self.__old = str([cue.properties() for cue in cues])

    def do(self):
        for cue in self.__cues:
            cue.update_properties(self.__new)

        self.__new = str(self.__new)

    def undo(self):
        for cue, old in zip(self.__cues, literal_eval(self.__old)):
            cue.update_properties(old)

    def redo(self):
        self.__new = literal_eval(self.__new)
        self.do()

    def log(self):
        return 'Cues configuration changed'
