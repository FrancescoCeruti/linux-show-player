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

from abc import abstractmethod


class Action:
    """Base class for actions.

    Action provides the ability to revert the changes done, calling "do" method,
    via "undo" method, and do them again via the "redo" method.
    An action could provide, via the "log" function, a simple log message.

    .. warning::
        Action shouldn't retains external object (e.g. cue(s), media(s))
        references. Use weak-references instead.
    """

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

    def log(self):
        """Used for logging

        :return: A log message
        :rtype: str
        """
        return ''
