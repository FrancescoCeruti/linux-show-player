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

import time
from threading import Event

from lisp.core.signal import Signal


class RWait:
    """Provide a resumeable-wait mechanism."""

    def __init__(self):
        self._elapsed = 0
        self._start_time = 0
        self._ended = False

        self._waiting = Event()
        self._waiting.set()
        self._is_waiting = Event()
        self._is_waiting.set()

        self.start = Signal()
        self.ended = Signal()
        self.paused = Signal()
        self.stopped = Signal()

    def wait(self, timeout, lock=None):
        """Block until the timeout is elapsed or `pause` or `stop` are called.

        If the wait is paused, the next time this function is called the timeout
        will be `total_timeout - elapsed_time`.

        :param timeout: time to wait
        :param lock: lock to release before and re-acquired after the wait
        :return: True if the wait has not been interrupted by `pause` or `stop`
        :rtype: bool
        """
        if self._is_waiting.is_set():
            # Clear the events
            self._waiting.clear()
            self._is_waiting.clear()
            # Set the start-time
            self._start_time = time.monotonic() - self._elapsed

            self.start.emit()

            if lock is not None:
                lock.release()

            # Wait for the "remaining" time
            self._ended = not self._waiting.wait(timeout - self._elapsed)

            # If the wait is ended by timeout
            if self._ended:
                self._elapsed = 0
                self.ended.emit()

            # Notify that we are not waiting anymore
            self._is_waiting.set()

            if lock is not None:
                lock.acquire()

            return self._ended

        return False

    def stop(self):
        """Stop the wait."""
        if self.current_time() > 0:
            self._waiting.set()
            self._is_waiting.wait()

            # Check self._ended to ensure that the wait is not ended by timeout
            # before `self._waiting.set()` is called in this method.
            if not self._ended:
                self._elapsed = 0
                self.stopped.emit()

    def pause(self):
        """Pause the wait."""
        if not self._is_waiting.is_set():
            # Calculate elapsed time ASAP
            elapsed = time.monotonic() - self._start_time
            self._waiting.set()
            self._is_waiting.wait()

            # Check self._ended to ensure that the wait is not ended by timeout
            # before `self._waiting.set()` is called in this method.
            if not self._ended:
                self._elapsed = elapsed
                self.paused.emit()

    def current_time(self):
        """Return the currently elapsed time."""
        if self._is_waiting.is_set():
            return self._elapsed

        return time.monotonic() - self._start_time

    def is_waiting(self):
        return not self._is_waiting.is_set()

    def is_paused(self):
        return self._is_waiting.is_set() and self.current_time() > 0
