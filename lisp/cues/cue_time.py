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

from enum import IntEnum
from weakref import WeakValueDictionary

from lisp.core.clock import Clock_100
from lisp.core.decorators import locked_method
from lisp.core.signal import Connection, Signal
from lisp.cues.cue import CueState


class MetaCueTime(type):
    """Allow "caching" of CueTime(s) objects."""

    __Instances = WeakValueDictionary()

    @locked_method
    def __call__(cls, cue, *args, **kwargs):
        instance = MetaCueTime.__Instances.get((cls, cue.id))
        if instance is None:
            instance = super().__call__(cue, *args, **kwargs)
            MetaCueTime.__Instances[(cls, cue.id)] = instance

        return instance


class CueTime(metaclass=MetaCueTime):
    """Provide timing for a Cue.

    Once created the notify signal provide timing for the given cue.
    The current time is queried using `Cue.current_time()`.

    .. note::
        The notify signal is emitted only when the cue is running.
    """

    _Clock = Clock_100

    def __init__(self, cue):
        self.notify = Signal()

        self._clock = self._Clock
        self._active = False
        self._cue = cue
        self._cue.changed("duration").connect(self.__init)

        self.__init()

    def __init(self, *args):
        if self._cue.duration > 0 and not self._active:
            # Cue "status" signals
            self._cue.started.connect(self.start, Connection.QtQueued)
            self._cue.paused.connect(self.stop, Connection.QtQueued)
            self._cue.stopped.connect(self.stop, Connection.QtQueued)
            self._cue.end.connect(self.stop, Connection.QtQueued)
            self._cue.error.connect(self.stop, Connection.QtQueued)

            if self._cue.state & CueState.Running:
                self.start()
            self._active = True
        elif self._cue.duration < 0 and self._active:
            self._cue.started.disconnect(self.start)
            self._cue.paused.disconnect(self.stop)
            self._cue.stopped.disconnect(self.stop)
            self._cue.end.disconnect(self.stop)
            self._cue.error.disconnect(self.stop)

            self.stop()
            self._active = False

    def __notify(self):
        """Notify the cue current-time"""
        if self._cue.state & (CueState.Running ^ CueState.Pause):
            self.notify.emit(self._cue.current_time())

    def start(self):
        self._clock.add_callback(self.__notify)

    def stop(self):
        try:
            self._clock.remove_callback(self.__notify)
        except Exception:
            # TODO: catch only the exception when the callback is not registered
            pass


class CueWaitTime:
    """Provide timing for Cue pre/post waits.

    Once created the notify signal provide timing for the specified wait for the
    given cue.
    The time since the wait start is calculated internally using the :mod:`time`
    module functions.
    """

    class Mode(IntEnum):
        Pre = 0
        Post = 1

    def __init__(self, cue, mode=Mode.Pre):
        self.notify = Signal()

        self._clock = Clock_100
        self._start_time = 0
        self._last = 0
        self._cue = cue
        self._mode = mode

        if self._mode == CueWaitTime.Mode.Pre:
            self._cue.prewait_ended.connect(self.stop, Connection.QtQueued)
            self._cue.prewait_start.connect(self.start, Connection.QtQueued)
            self._cue.prewait_paused.connect(self.stop, Connection.QtQueued)
            self._cue.prewait_stopped.connect(self.stop, Connection.QtQueued)
        elif self._mode == CueWaitTime.Mode.Post:
            self._cue.postwait_ended.connect(self.stop, Connection.QtQueued)
            self._cue.postwait_start.connect(self.start, Connection.QtQueued)
            self._cue.postwait_paused.connect(self.stop, Connection.QtQueued)
            self._cue.postwait_stopped.connect(self.stop, Connection.QtQueued)

    def __notify(self):
        if self._mode == CueWaitTime.Mode.Pre:
            self.notify.emit(int(self._cue.prewait_time() * 100) * 10)
        else:
            self.notify.emit(int(self._cue.postwait_time() * 100) * 10)

    def start(self):
        self._clock.add_callback(self.__notify)

    def stop(self):
        try:
            self._clock.remove_callback(self.__notify)
        except Exception:
            # TODO: catch only the exception when the callback is not registered
            pass
