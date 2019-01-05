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

from lisp.core.signal import Signal


class Protocol:
    """Base interface for protocols.

    The init() and reset() functions are called when a session is created
    and deleted.

    When an event that can trigger a cue is "detected", the protocol_event
    signal should be emitted with the event representation.

    To be loaded correctly the class should follow the ClassesLoader
    specification.
    """

    CueSettings = None
    LayoutSettings = None

    def __init__(self):
        self.protocol_event = Signal()

    def init(self):
        pass

    def reset(self):
        pass
