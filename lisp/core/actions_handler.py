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

import logging
from collections import deque

from lisp.core import configuration as cfg
from lisp.core.action import Action
from lisp.core.signal import Signal


class ActionsHandler:
    """Provide a classic undo/redo mechanism based on stacks."""

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

        self._saved_action = None

    def clear(self):
        """Clear the `undo` and `redo` stacks."""
        self._undo.clear()
        self._redo.clear()
        self._saved_action = None

    def do_action(self, action: Action):
        """Execute the action, and add it the `undo` stack.

        When an action is executed:
         * is logged
         * is appended to the `undo` stack
         * the `redo` stack is cleared to maintain consistency
         * the `action_done` signal is emitted
        """
        action.do()

        self._logging(action, 'Last action: ')
        self._undo.append(action)
        # Clean the redo stack for maintain consistency
        self._redo.clear()

        self.action_done.emit(action)

    def undo_action(self):
        """Undo the last executed action, and add it to the `redo` stack.

        When an action is undone:
         * is removed from the `undo` stack
         * is logged
         * is appended to the `redo` stack
         * the signal `action_undone` is emitted
        """
        if self._undo:
            action = self._undo.pop()
            action.undo()

            self._logging(action, 'Undo: ')
            self._redo.append(action)

            self.action_undone.emit(action)

    def redo_action(self):
        """Redo the last undone action, and add it back to the `undo` stack.

        When an action is redone:
         * is remove from the `redo` stack
         * is logged
         * is added to the `undo` stack
         * the `action_redone` signal is emitted
        """
        if self._redo:
            action = self._redo.pop()
            action.redo()

            self._logging(action, 'Redo: ')
            self._undo.append(action)

            self.action_redone.emit(action)

    def set_saved(self):
        """Set the action at the _top_ of the `undo` stack as `save-point`."""
        if self._undo:
            self._saved_action = self._undo[-1]

    def is_saved(self) -> bool:
        """Return True if the action at the _top_ of the `undo` stack is the
        `save-point`.
        """
        if self._undo:
            return self._undo[-1] is self._saved_action
        else:
            return True

    @staticmethod
    def _logging(action: Action, pre: str):
        message = action.log()
        if message.strip() == '':
            message = type(action).__name__

        logging.info(pre + message)


MainActionsHandler = ActionsHandler()  # "global" action-handler
