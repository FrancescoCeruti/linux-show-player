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

from lisp.backends.base.media import MediaState
from lisp.core.clock import Clock
from lisp.core.signal import Connection, Signal


class MediaTime:

    def __init__(self, media):
        super().__init__()

        self.notify = Signal() # (int)

        self._media = media
        self._clock = Clock()

        # Media "status" signals
        self._media.on_play.connect(self._start, mode=Connection.QtQueued)
        self._media.paused.connect(self._stop, mode=Connection.QtQueued)
        self._media.stopped.connect(self._stop, mode=Connection.QtQueued)
        self._media.interrupted.connect(self._stop, mode=Connection.QtQueued)
        self._media.error.connect(self._stop, mode=Connection.QtQueued)
        self._media.eos.connect(self._stop, mode=Connection.QtQueued)

        if self._media.state == MediaState.Playing:
            self._start()

    def _notify(self):
        """Notify the current media time"""
        self.notify.emit(self._media.current_time())

    def _start(self):
        self._clock.add_callback(self._notify)

    def _stop(self):
        try:
            self._clock.remove_callback(self._notify)
        except Exception:
            pass
