# This file is part of Linux Show Player
#
# Copyright 2022 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import QRect, QSize, Qt
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QFontDatabase,
    QPainter,
    QPainterPath,
    QPen,
)
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

        # This value will be used to provide some spacing for the widget
        # the value depends on the current font.
        self.sizeIncrement = QSize(
            self.fontMetrics().size(Qt.TextSingleLine, "00").width(), 0
        )

        item.cue.changed("index").connect(self.__update, Connection.QtQueued)
        self.__update(item.cue.index)

    def sizeHint(self):
        return super().sizeHint() + self.sizeIncrement

    def __update(self, newIndex):
        self.setText(str(newIndex + 1))


class NameWidget(QLabel):
    def __init__(self, item, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._item = item
        self._item.cue.changed("name").connect(
            self.__update, Connection.QtQueued
        )

        self.setText(self._item.cue.name)

    def __update(self, text):
        super().setText(text)


class CueStatusIcons(QWidget):
    MARGIN = 5

    def __init__(self, item, *args):
        super().__init__(*args)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._icon = None
        self._item = item

        self._item.cue.changed("icon").connect(
            self.updateIcon, Connection.QtQueued
        )
        self._item.cue.interrupted.connect(self.updateIcon, Connection.QtQueued)
        self._item.cue.started.connect(self.updateIcon, Connection.QtQueued)
        self._item.cue.stopped.connect(self.updateIcon, Connection.QtQueued)
        self._item.cue.paused.connect(self.updateIcon, Connection.QtQueued)
        self._item.cue.error.connect(self.updateIcon, Connection.QtQueued)
        self._item.cue.end.connect(self.updateIcon, Connection.QtQueued)

        self.updateIcon()

    def updateIcon(self):
        if self._item.cue.state & CueState.Running:
            self._icon = IconTheme.get(f"{self._item.cue.icon}-running")
        elif self._item.cue.state & CueState.Pause:
            self._icon = IconTheme.get(f"{self._item.cue.icon}-pause")
        elif self._item.cue.state & CueState.Error:
            self._icon = IconTheme.get(f"{self._item.cue.icon}-error")
        else:
            self._icon = IconTheme.get(self._item.cue.icon)

        self.update()

    def _size(self):
        return self.height() - CueStatusIcons.MARGIN * 2

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.HighQualityAntialiasing, True)

        status_size = self._size()
        indicator_height = self.height()
        indicator_width = indicator_height // 2

        if self._item.current:
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
            path.lineTo(indicator_width // 3, 1)
            path.lineTo(0, 1)

            qp.setPen(QPen(QBrush(QColor(0, 0, 0)), 2))
            qp.setBrush(QBrush(QColor(250, 220, 0)))
            qp.drawPath(path)
        if self._icon is not None:
            qp.drawPixmap(
                QRect(
                    indicator_width + CueStatusIcons.MARGIN,
                    CueStatusIcons.MARGIN,
                    status_size,
                    status_size,
                ),
                self._icon.pixmap(self._size()),
            )

        qp.end()


class NextActionIcon(QLabel):
    SIZE = 16

    def __init__(self, item, *args):
        super().__init__(*args)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAlignment(Qt.AlignCenter)

        item.cue.changed("next_action").connect(
            self._updateIcon, Connection.QtQueued
        )
        self._updateIcon(item.cue.next_action)

    def _updateIcon(self, nextAction):
        nextAction = CueNextAction(nextAction)
        pixmap = IconTheme.get("").pixmap(self.SIZE)

        if (
            nextAction == CueNextAction.TriggerAfterWait
            or nextAction == CueNextAction.TriggerAfterEnd
        ):
            pixmap = IconTheme.get("cue-trigger-next").pixmap(self.SIZE)
        elif (
            nextAction == CueNextAction.SelectAfterWait
            or nextAction == CueNextAction.SelectAfterEnd
        ):
            pixmap = IconTheme.get("cue-select-next").pixmap(self.SIZE)

        self.setToolTip(tr_next_action(nextAction))
        self.setPixmap(pixmap)


class TimeWidget(QProgressBar):
    def __init__(self, item, *args):
        super().__init__(*args)
        self.setObjectName("ListTimeWidget")
        self.setValue(0)
        self.setTextVisible(True)
        self.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))

        self.cue = item.cue
        self.duration = 0
        self.showZeroDuration = False

    def _updateTime(self, time):
        self.setValue(time)
        self.setFormat(strtime(time, accurate=1))

    def _updateDuration(self, duration):
        self.duration = duration

        if duration > 0 or self.showZeroDuration:
            # Display as disabled if duration < 0
            self.setEnabled(duration > 0)
            self.setTextVisible(True)
            self.setFormat(strtime(duration, accurate=2))
            # Avoid settings min and max to 0, or the bar go in busy state
            self.setRange(0 if duration > 0 else -1, int(duration))
        else:
            self.setTextVisible(False)

    def _updateStyle(self, state):
        self.setProperty("state", state)
        self.style().unpolish(self)
        self.style().polish(self)

    def _running(self):
        self._updateStyle("running")

    def _pause(self):
        self._updateStyle("pause")
        self._updateTime(self.value())

    def _stop(self):
        self._updateStyle("stop")
        self.setValue(self.minimum())

    def _error(self):
        self._updateStyle("error")
        self.setValue(self.minimum())


class CueTimeWidget(TimeWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self._updateDuration(self.cue.duration)

        self.cue.interrupted.connect(self._stop, Connection.QtQueued)
        self.cue.started.connect(self._running, Connection.QtQueued)
        self.cue.stopped.connect(self._stop, Connection.QtQueued)
        self.cue.paused.connect(self._pause, Connection.QtQueued)
        self.cue.error.connect(self._error, Connection.QtQueued)
        self.cue.end.connect(self._stop, Connection.QtQueued)
        self.cue.changed("duration").connect(
            self._updateDuration, Connection.QtQueued
        )

        self.cueTime = CueTime(self.cue)
        self.cueTime.notify.connect(self._updateTime, Connection.QtQueued)

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
        self._updateDuration(self.cue.duration)


class PreWaitWidget(TimeWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self.showZeroDuration = True
        self._updateDuration(self.cue.pre_wait)

        self.cue.prewait_start.connect(self._running, Connection.QtQueued)
        self.cue.prewait_stopped.connect(self._stop, Connection.QtQueued)
        self.cue.prewait_paused.connect(self._pause, Connection.QtQueued)
        self.cue.prewait_ended.connect(self._stop, Connection.QtQueued)
        self.cue.changed("pre_wait").connect(
            self._updateDuration, Connection.QtQueued
        )

        self.waitTime = CueWaitTime(self.cue, mode=CueWaitTime.Mode.Pre)
        self.waitTime.notify.connect(self._updateTime, Connection.QtQueued)

    def _updateTime(self, time):
        self.setValue(time)
        self.setFormat(strtime(self.duration - time, accurate=1))

    def _updateDuration(self, duration):
        # The wait time is in seconds, we need milliseconds
        super()._updateDuration(duration * 1000)

    def _stop(self):
        super()._stop()
        self._updateDuration(self.cue.pre_wait)


class PostWaitWidget(TimeWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self.showZeroDuration = True

        self.cue.changed("next_action").connect(
            self._nextActionChanged, Connection.QtQueued
        )

        self.waitTime = CueWaitTime(self.cue, mode=CueWaitTime.Mode.Post)
        self.cueTime = CueTime(self.cue)

        self._nextActionChanged(self.cue.next_action)

    def _updateTime(self, time):
        self.setValue(time)
        self.setFormat(strtime(self.duration - time, accurate=1))

    def _updateDuration(self, duration):
        if (
            self.cue.next_action == CueNextAction.TriggerAfterWait
            or self.cue.next_action == CueNextAction.SelectAfterWait
        ):
            # The wait time is in seconds, we need milliseconds
            duration *= 1000

        super()._updateDuration(duration)

    def _nextActionChanged(self, nextAction):
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

        self.cueTime.notify.disconnect(self._updateTime)
        self.waitTime.notify.disconnect(self._updateTime)

        self.cue.changed("post_wait").disconnect(self._updateDuration)
        self.cue.changed("duration").disconnect(self._updateDuration)

        if (
            nextAction == CueNextAction.TriggerAfterEnd
            or nextAction == CueNextAction.SelectAfterEnd
        ):
            self.cue.interrupted.connect(self._stop, Connection.QtQueued)
            self.cue.started.connect(self._running, Connection.QtQueued)
            self.cue.stopped.connect(self._stop, Connection.QtQueued)
            self.cue.paused.connect(self._pause, Connection.QtQueued)
            self.cue.error.connect(self._stop, Connection.QtQueued)
            self.cue.end.connect(self._stop, Connection.QtQueued)
            self.cue.changed("duration").connect(
                self._updateDuration, Connection.QtQueued
            )

            self.cueTime.notify.connect(self._updateTime, Connection.QtQueued)
            self._updateDuration(self.cue.duration)
        else:
            self.cue.postwait_start.connect(self._running, Connection.QtQueued)
            self.cue.postwait_stopped.connect(self._stop, Connection.QtQueued)
            self.cue.postwait_paused.connect(self._pause, Connection.QtQueued)
            self.cue.postwait_ended.connect(self._stop, Connection.QtQueued)
            self.cue.changed("post_wait").connect(
                self._updateDuration, Connection.QtQueued
            )

            self.waitTime.notify.connect(self._updateTime, Connection.QtQueued)
            self._updateDuration(self.cue.post_wait)

    def _stop(self):
        super()._stop()

        if (
            self.cue.next_action == CueNextAction.TriggerAfterEnd
            or self.cue.next_action == CueNextAction.SelectAfterEnd
        ):
            self._updateDuration(self.cue.duration)
        else:
            self._updateDuration(self.cue.post_wait)
