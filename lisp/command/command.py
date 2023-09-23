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

from abc import ABC, abstractmethod


class Command(ABC):
    """Base class for commands.

    A Command gives the ability to revert the changes done in the "do" method,
    via the "undo" method, and redo them via the "redo" method.

    A simple log message can be provided, via the "log" function.

    .. warning::
        Commands may keep reference to external objects.
    """

    __slots__ = ()

    @abstractmethod
    def do(self):
        """Do something"""

    @abstractmethod
    def undo(self):
        """Revert what do function has done"""

    def redo(self):
        """Redo after reverting

        The default implementation call the "do" function.
        """
        self.do()

    def log(self) -> str:
        """Return a short message to describe what the command does.

        The method should return a message generic for do/undo/redo,
        a handler will care about adding context to the message.

        The log message should be user-friendly and localized.
        """
        return ""
