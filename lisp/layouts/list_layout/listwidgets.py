# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2017 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QLabel, QProgressBar

from lisp.core.signal import Connection
from lisp.core.util import strtime
from lisp.cues.cue import CueNextAction, CueState
from lisp.cues.cue_time import CueTime, CueWaitTime
from lisp.ui.ui_utils import pixmap_from_icon


class CueStatusIcon(QLabel):
    STYLESHEET = 'background: transparent; padding-left: 20px;'
    SIZE = 16

    def __init__(self, cue, *args):
        super().__init__(*args)
        self.setStyleSheet(CueStatusIcon.STYLESHEET)

        self.cue = cue
        self.cue.interrupted.connect(self._stop, Connection.QtQueued)
        self.cue.started.connect(self._start, Connection.QtQueued)
        self.cue.stopped.connect(self._stop, Connection.QtQueued)
        self.cue.paused.connect(self._pause, Connection.QtQueued)
        self.cue.error.connect(self._error, Connection.QtQueued)
        self.cue.end.connect(self._stop, Connection.QtQueued)

    def _start(self):
        self.setPixmap(pixmap_from_icon('led-running', self.SIZE))

    def _pause(self):
        self.setPixmap(pixmap_from_icon('led-pause', self.SIZE))

    def _error(self, *args):
        self.setPixmap(pixmap_from_icon('led-error', self.SIZE))

    def _stop(self):
        self.setPixmap(pixmap_from_icon('', self.SIZE))

    def sizeHint(self):
        return QSize(self.SIZE, self.SIZE)


class NextActionIcon(QLabel):
    STYLESHEET = 'background: transparent; padding-left: 1px'
    SIZE = 16

    def __init__(self, cue, *args):
        super().__init__(*args)
        self.setStyleSheet(self.STYLESHEET)

        self.cue = cue
        self.cue.changed('next_action').connect(
            self._update_icon, Connection.QtQueued)

        self._update_icon(self.cue.next_action)

    def _update_icon(self, next_action):
        next_action = CueNextAction(next_action)
        pixmap = pixmap_from_icon('', self.SIZE)

        if next_action == CueNextAction.AutoNext:
            pixmap = pixmap_from_icon('auto-next', self.SIZE)
            self.setToolTip(CueNextAction.AutoNext.value)
        elif next_action == CueNextAction.AutoFollow:
            pixmap = pixmap_from_icon('auto-follow', self.SIZE)
            self.setToolTip(CueNextAction.AutoFollow.value)
        else:
            self.setToolTip('')

        self.setPixmap(pixmap)

    def sizeHint(self):
        return QSize(self.SIZE + 2, self.SIZE)


class TimeWidget(QProgressBar):

    def __init__(self, cue, *args):
        super().__init__(*args)
        self.setObjectName('ListTimeWidget')
        self.setValue(0)
        self.setTextVisible(True)

        self.show_zero_duration = False
        self.accurate_time = True
        self.cue = cue

    def _update_time(self, time):
        self.setValue(time)
        self.setFormat(strtime(time, accurate=self.accurate_time))

    def _update_duration(self, duration):
        if duration > 0 or self.show_zero_duration:
            # Display as disabled if duration < 0
            self.setEnabled(duration > 0)
            self.setTextVisible(True)
            self.setFormat(strtime(duration, accurate=self.accurate_time))
            # Avoid settings min and max to 0, or the the bar go in busy state
            self.setRange(0 if duration > 0 else -1, duration)
        else:
            self.setTextVisible(False)

    def _update_style(self, state):
        self.setProperty('state', state)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _running(self):
        self._update_style('running')

    def _pause(self):
        self._update_style('pause')
        self._update_time(self.value())

    def _stop(self):
        self._update_style('stop')
        self.setValue(self.minimum())

    def _error(self):
        self._update_style('error')
        self.setValue(self.minimum())


class CueTimeWidget(TimeWidget):

    def __init__(self, cue, *args):
        super().__init__(cue, *args)

        self.cue.interrupted.connect(self._stop, Connection.QtQueued)
        self.cue.started.connect(self._running, Connection.QtQueued)
        self.cue.stopped.connect(self._stop, Connection.QtQueued)
        self.cue.paused.connect(self._pause, Connection.QtQueued)
        self.cue.error.connect(self._error, Connection.QtQueued)
        self.cue.end.connect(self._stop, Connection.QtQueued)
        self.cue.changed('duration').connect(
            self._update_duration, Connection.QtQueued)

        self.cue_time = CueTime(self.cue)
        self.cue_time.notify.connect(self._update_time, Connection.QtQueued)

        if cue.state & CueState.Running:
            self._running()
        elif cue.state & CueState.Pause:
            self._pause()
        elif cue.state & CueState.Error:
            self._error()
        else:
            self._stop()

    def _stop(self):
        super()._stop()
        self._update_duration(self.cue.duration)


class PreWaitWidget(TimeWidget):

    def __init__(self, cue, *args):
        super().__init__(cue, *args)
        self.show_zero_duration = True

        self.cue.prewait_start.connect(self._running, Connection.QtQueued)
        self.cue.prewait_stopped.connect(self._stop, Connection.QtQueued)
        self.cue.prewait_paused.connect(self._pause, Connection.QtQueued)
        self.cue.prewait_ended.connect(self._stop, Connection.QtQueued)
        self.cue.changed('pre_wait').connect(
            self._update_duration, Connection.QtQueued)

        self._update_duration(self.cue.pre_wait)

        self.wait_time = CueWaitTime(self.cue, mode=CueWaitTime.Mode.Pre)
        self.wait_time.notify.connect(self._update_time, Connection.QtQueued)

    def _update_duration(self, duration):
        # The wait time is in seconds, we need milliseconds
        super()._update_duration(duration * 1000)

    def _stop(self):
        super()._stop()
        self._update_duration(self.cue.pre_wait)


class PostWaitWidget(TimeWidget):

    def __init__(self, cue, *args):
        super().__init__(cue, *args)
        self.show_zero_duration = True

        self.cue.changed('next_action').connect(
            self._next_action_changed, Connection.QtQueued)

        self.wait_time = CueWaitTime(self.cue, mode=CueWaitTime.Mode.Post)
        self.cue_time = CueTime(self.cue)

        self._next_action_changed(self.cue.next_action)

    def _update_duration(self, duration):
        if self.cue.next_action != CueNextAction.AutoFollow.value:
            # The wait time is in seconds, we need milliseconds
            duration *= 1000

        super()._update_duration(duration)

    def _next_action_changed(self, next_action):
        self.cue.postwait_start.disconnect(self._running)
        self.cue.postwait_stopped.disconnect(self._stop)
        self.cue.postwait_paused.disconnect(self._pause)
        self.cue.postwait_ended.disconnect(self._stop)

        self.cue.interrupted.disconnect(self._stop)
        self.cue.started.disconnect(self._running)
        self.cue.stopped.disconnect(self._stop)
        self.cue.paused.disconnect(self._pause)
        self.cue.error.disconnect(self._stop)
        self.cue.end.disconnect(self._stop)

        self.cue_time.notify.disconnect(self._update_time)
        self.wait_time.notify.disconnect(self._update_time)

        self.cue.changed('post_wait').disconnect(self._update_duration)
        self.cue.changed('duration').disconnect(self._update_duration)

        if next_action == CueNextAction.AutoFollow.value:
            self.cue.interrupted.connect(self._stop, Connection.QtQueued)
            self.cue.started.connect(self._running, Connection.QtQueued)
            self.cue.stopped.connect(self._stop, Connection.QtQueued)
            self.cue.paused.connect(self._pause, Connection.QtQueued)
            self.cue.error.connect(self._stop, Connection.QtQueued)
            self.cue.end.connect(self._stop, Connection.QtQueued)
            self.cue.changed('duration').connect(
                self._update_duration, Connection.QtQueued)

            self.cue_time.notify.connect(self._update_time, Connection.QtQueued)
            self._update_duration(self.cue.duration)
        else:
            self.cue.postwait_start.connect(self._running, Connection.QtQueued)
            self.cue.postwait_stopped.connect(self._stop, Connection.QtQueued)
            self.cue.postwait_paused.connect(self._pause, Connection.QtQueued)
            self.cue.postwait_ended.connect(self._stop, Connection.QtQueued)
            self.cue.changed('post_wait').connect(
                self._update_duration, Connection.QtQueued)

            self.wait_time.notify.connect(
                self._update_time, Connection.QtQueued)
            self._update_duration(self.cue.post_wait)

    def _stop(self):
        super()._stop()

        if self.cue.next_action == CueNextAction.AutoFollow.value:
            self._update_duration(self.cue.duration)
        else:
            self._update_duration(self.cue.post_wait)