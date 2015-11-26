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


import logging
from collections import deque

from lisp.core.signal import Signal
from lisp.core.singleton import Singleton
from lisp.utils import configuration as cfg


class ActionsHandler:
    """Do/Undo/Redo actions and store the in stacks.

    Provide methods for using actions, an storing them in stacks, allowing
    to undo and redo actions.
    """
    MaxStackSize = int(cfg.config['Actions']['MaxStackSize'])

    def __init__(self):
        super().__init__()

        self.action_done = Signal()
        self.action_undone = Signal()
        self.action_redone = Signal()

        self._undo = deque()
        self._redo = deque()
        if self.MaxStackSize > 0:
            self._undo.maxlen = self.MaxStackSize
            self._redo.maxlen = self.MaxStackSize

        self._saved = False
        self._saved_action = None

    def clear(self):
        self._undo.clear()
        self._redo.clear()
        self._saved_action = None

    def do_action(self, action):
        action.do()

        self._logging(action, 'Last action: ')
        self._undo.append(action)
        # Clean the redo stack for maintain consistency
        self._redo.clear()
        self._saved = False

        self.action_done.emit(action)

    def undo_action(self):
        if self._undo:
            action = self._undo.pop()
            action.undo()

            self._logging(action, 'Undo: ')
            self._redo.append(action)
            self._saved = False

            self.action_undone.emit(action)

    def redo_action(self):
        if self._redo:
            action = self._redo.pop()
            action.redo()

            self._logging(action, 'Redo: ')
            self._undo.append(action)
            self._saved = False

            self.action_redone.emit(action)

    def set_saved(self):
        self._saved = True
        if self._undo:
            self._saved_action = self._undo[-1]

    def is_saved(self):
        if self._undo:
            return self._saved or self._undo[-1] is self._saved_action
        else:
            return True

    def _logging(self, action, pre, ):
        message = action.log()
        if message.strip() == '':
            message = type(action).__name__

        logging.info(pre + message)


class MainActionsHandler(ActionsHandler, metaclass=Singleton):
    pass
