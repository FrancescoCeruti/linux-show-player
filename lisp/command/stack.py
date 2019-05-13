# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from lisp.command.command import Command
from lisp.core.signal import Signal
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class CommandsStack:
    """Provide a classic undo/redo mechanism based on stacks."""

    DO_STR = "{}"
    UNDO_STR = translate("CommandsStack", "Undo: {}")
    REDO_STR = translate("CommandsStack", "Redo: {}")

    def __init__(self, stack_size=None):
        super().__init__()

        self._undo = deque(maxlen=stack_size)
        self._redo = deque(maxlen=stack_size)
        self._saved = None

        self.done = Signal()
        self.saved = Signal()
        self.undone = Signal()
        self.redone = Signal()

    def clear(self):
        """Clear the `undo`, `redo` stacks and the save status."""
        self._undo.clear()
        self._redo.clear()
        self._saved = None

    def do(self, command: Command):
        """Execute the command, and add it the `undo` stack."""
        command.do()

        self._logging(command, CommandsStack.DO_STR)
        self._undo.append(command)
        # Clean the redo stack for maintain consistency
        self._redo.clear()

        self.done.emit(command)

    def undo_last(self):
        """Undo the last executed command, and add it to the `redo` stack."""
        if self._undo:
            command = self._undo.pop()
            command.undo()

            self._logging(command, CommandsStack.UNDO_STR)
            self._redo.append(command)

            self.undone.emit(command)

    def redo_last(self):
        """Redo the last undone command, and add it back to the `undo` stack."""
        if self._redo:
            command = self._redo.pop()
            command.redo()

            self._logging(command, CommandsStack.REDO_STR)
            self._undo.append(command)

            self.redone.emit(command)

    def set_saved(self):
        """Set the command at the _top_ of the `undo` stack as `save-point`."""
        if self._undo:
            self._saved = self._undo[-1]
            self.saved.emit()

    def is_saved(self) -> bool:
        """Return True if the command at the _top_ of the `undo` stack is the
        one that was on the _top_ of stack the last time `set_saved()`
        as been called.
        """
        if self._undo:
            return self._undo[-1] is self._saved

        return True

    @staticmethod
    def _logging(command: Command, template: str):
        message = command.log()
        if message:
            logger.info(template.format(message))
