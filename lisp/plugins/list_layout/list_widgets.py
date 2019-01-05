# This file is part of Linux Show Player
#
# Copyright 2017 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QFont, QPainter, QBrush, QColor, QPen, QPainterPath
from PyQt5.QtWidgets import QLabel, QProgressBar, QWidget

from lisp.core.signal import Connection
from lisp.core.util import strtime
from lisp.cues.cue import CueNextAction, CueState
from lisp.cues.cue_time import CueTime, CueWaitTime
from lisp.ui.icons import IconTheme
from lisp.ui.widgets.cue_next_actions import tr_next_action


class IndexWidget(QLabel):
    def __init__(self, item, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAlignment(Qt.AlignCenter)

        item.cue.changed("index").connect(self.__update, Connection.QtQueued)
        self.__update(item.cue.index)

    def __update(self, newIndex):
        self.setText(str(newIndex + 1))


class NameWidget(QLabel):
    def __init__(self, item, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_TranslucentBackground)

        item.cue.changed("name").connect(self.__update, Connection.QtQueued)
        self.__update(item.cue.name)

    def __update(self, newName):
        self.setText(newName)


class CueStatusIcons(QWidget):
    MARGIN = 6

    def __init__(self, item, *args):
        super().__init__(*args)
        self._statusPixmap = None

        self.item = item
        self.item.cue.interrupted.connect(self._stop, Connection.QtQueued)
        self.item.cue.started.connect(self._start, Connection.QtQueued)
        self.item.cue.stopped.connect(self._stop, Connection.QtQueued)
        self.item.cue.paused.connect(self._pause, Connection.QtQueued)
        self.item.cue.error.connect(self._error, Connection.QtQueued)
        self.item.cue.end.connect(self._stop, Connection.QtQueued)

    def setPixmap(self, pixmap):
        self._statusPixmap = pixmap
        self.update()

    def _standbyChange(self):
        self.update()

    def _start(self):
        self.setPixmap(IconTheme.get("led-running").pixmap(self._size()))

    def _pause(self):
        self.setPixmap(IconTheme.get("led-pause").pixmap(self._size()))

    def _error(self):
        self.setPixmap(IconTheme.get("led-error").pixmap(self._size()))

    def _stop(self):
        self.setPixmap(None)

    def _size(self):
        return self.height() - CueStatusIcons.MARGIN * 2

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.HighQualityAntialiasing, True)

        status_size = self._size()
        indicator_height = self.height()
        indicator_width = indicator_height // 2

        if self.item.current:
            # Draw something like this
            # |‾\
            # |  \
            # |  /
            # |_/
            path = QPainterPath()
            path.moveTo(0, 1)
            path.lineTo(0, indicator_height - 1)
            path.lineTo(indicator_width // 3, indicator_height - 1)
            path.lineTo(indicator_width, indicator_width)
            path.lineTo(indicator_width // 3, 0)
            path.lineTo(0, 1)

            qp.setPen(QPen(QBrush(QColor(0, 0, 0)), 2))
            qp.setBrush(QBrush(QColor(250, 220, 0)))
            qp.drawPath(path)
        if self._statusPixmap is not None:
            qp.drawPixmap(
                QRect(
                    indicator_width + CueStatusIcons.MARGIN,
                    CueStatusIcons.MARGIN,
                    status_size,
                    status_size,
                ),
                self._statusPixmap,
            )

        qp.end()


class NextActionIcon(QLabel):
    STYLESHEET = "background: transparent;"
    SIZE = 16

    def __init__(self, item, *args):
        super().__init__(*args)
        self.setStyleSheet(self.STYLESHEET)
        self.setAlignment(Qt.AlignCenter)

        item.cue.changed("next_action").connect(
            self.__update, Connection.QtQueued
        )
        self.__update(item.cue.next_action)

    def __update(self, next_action):
        next_action = CueNextAction(next_action)
        pixmap = IconTheme.get("").pixmap(self.SIZE)

        if (
            next_action == CueNextAction.TriggerAfterWait
            or next_action == CueNextAction.TriggerAfterEnd
        ):
            pixmap = IconTheme.get("cue-trigger-next").pixmap(self.SIZE)
        elif (
            next_action == CueNextAction.SelectAfterWait
            or next_action == CueNextAction.SelectAfterEnd
        ):
            pixmap = IconTheme.get("cue-select-next").pixmap(self.SIZE)

        self.setToolTip(tr_next_action(next_action))

        self.setPixmap(pixmap)


class TimeWidget(QProgressBar):
    def __init__(self, item, *args):
        super().__init__(*args)
        self.setObjectName("ListTimeWidget")
        self.setValue(0)
        self.setTextVisible(True)
        font = QFont("Monospace")
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

        self.show_zero_duration = False
        self.accurate_time = True
        self.cue = item.cue

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
        self.setProperty("state", state)
        self.style().unpolish(self)
        self.style().polish(self)

    def _running(self):
        self._update_style("running")

    def _pause(self):
        self._update_style("pause")
        self._update_time(self.value())

    def _stop(self):
        self._update_style("stop")
        self.setValue(self.minimum())

    def _error(self):
        self._update_style("error")
        self.setValue(self.minimum())


class CueTimeWidget(TimeWidget):
    def __init__(self, *args):
        super().__init__(*args)

        self.cue.interrupted.connect(self._stop, Connection.QtQueued)
        self.cue.started.connect(self._running, Connection.QtQueued)
        self.cue.stopped.connect(self._stop, Connection.QtQueued)
        self.cue.paused.connect(self._pause, Connection.QtQueued)
        self.cue.error.connect(self._error, Connection.QtQueued)
        self.cue.end.connect(self._stop, Connection.QtQueued)
        self.cue.changed("duration").connect(
            self._update_duration, Connection.QtQueued
        )

        self.cue_time = CueTime(self.cue)
        self.cue_time.notify.connect(self._update_time, Connection.QtQueued)

        if self.cue.state & CueState.Running:
            self._running()
        elif self.cue.state & CueState.Pause:
            self._pause()
        elif self.cue.state & CueState.Error:
            self._error()
        else:
            self._stop()

    def _stop(self):
        super()._stop()
        self._update_duration(self.cue.duration)


class PreWaitWidget(TimeWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self.show_zero_duration = True

        self.cue.prewait_start.connect(self._running, Connection.QtQueued)
        self.cue.prewait_stopped.connect(self._stop, Connection.QtQueued)
        self.cue.prewait_paused.connect(self._pause, Connection.QtQueued)
        self.cue.prewait_ended.connect(self._stop, Connection.QtQueued)
        self.cue.changed("pre_wait").connect(
            self._update_duration, Connection.QtQueued
        )

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
    def __init__(self, *args):
        super().__init__(*args)
        self.show_zero_duration = True

        self.cue.changed("next_action").connect(
            self._next_action_changed, Connection.QtQueued
        )

        self.wait_time = CueWaitTime(self.cue, mode=CueWaitTime.Mode.Post)
        self.cue_time = CueTime(self.cue)

        self._next_action_changed(self.cue.next_action)

    def _update_duration(self, duration):
        if (
            self.cue.next_action == CueNextAction.TriggerAfterWait
            or self.cue.next_action == CueNextAction.SelectAfterWait
        ):
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

        self.cue.changed("post_wait").disconnect(self._update_duration)
        self.cue.changed("duration").disconnect(self._update_duration)

        if (
            next_action == CueNextAction.TriggerAfterEnd
            or next_action == CueNextAction.SelectAfterEnd
        ):
            self.cue.interrupted.connect(self._stop, Connection.QtQueued)
            self.cue.started.connect(self._running, Connection.QtQueued)
            self.cue.stopped.connect(self._stop, Connection.QtQueued)
            self.cue.paused.connect(self._pause, Connection.QtQueued)
            self.cue.error.connect(self._stop, Connection.QtQueued)
            self.cue.end.connect(self._stop, Connection.QtQueued)
            self.cue.changed("duration").connect(
                self._update_duration, Connection.QtQueued
            )

            self.cue_time.notify.connect(self._update_time, Connection.QtQueued)
            self._update_duration(self.cue.duration)
        else:
            self.cue.postwait_start.connect(self._running, Connection.QtQueued)
            self.cue.postwait_stopped.connect(self._stop, Connection.QtQueued)
            self.cue.postwait_paused.connect(self._pause, Connection.QtQueued)
            self.cue.postwait_ended.connect(self._stop, Connection.QtQueued)
            self.cue.changed("post_wait").connect(
                self._update_duration, Connection.QtQueued
            )

            self.wait_time.notify.connect(
                self._update_time, Connection.QtQueued
            )
            self._update_duration(self.cue.post_wait)

    def _stop(self):
        super()._stop()

        if (
            self.cue.next_action == CueNextAction.TriggerAfterEnd
            or self.cue.next_action == CueNextAction.SelectAfterEnd
        ):
            self._update_duration(self.cue.duration)
        else:
            self._update_duration(self.cue.post_wait)
