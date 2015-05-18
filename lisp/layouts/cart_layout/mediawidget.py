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

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QProgressBar, QLCDNumber, QLabel

from lisp.backends.base.media import MediaState
from lisp.core.signal import Connection
from lisp.ui.qclickslider import QClickSlider
from lisp.backends.base.media_time import MediaTime
from lisp.layouts.cart_layout.cuewidget import CueWidget
from lisp.ui.qdbmeter import QDbMeter
from lisp.ui.qmessagebox import QDetailedMessageBox
from lisp.utils.util import strtime


class MediaCueWidget(CueWidget):
    STOPPED = QIcon.fromTheme("led_off")
    PAUSED = QIcon.fromTheme("led_yellow")
    PLAYING = QIcon.fromTheme("led_green")
    ERROR = QIcon.fromTheme("led_red")

    def __init__(self, **kwarg):
        super().__init__(**kwarg)

        self.fade = None

        self._accurate_timing = False
        self._show_dbmeter = False
        self._countdown_mode = True
        self._dbmeter_element = None

        self.seekSlider = QClickSlider(self)
        self.seekSlider.setOrientation(Qt.Horizontal)
        self.seekSlider.setFocusPolicy(Qt.NoFocus)
        self.seekSlider.setVisible(False)

        self.dbmeter = QDbMeter(self)
        self.dbmeter.setVisible(False)

        self.timeBar = QProgressBar(self)
        self.timeBar.setTextVisible(False)
        self.timeDisplay = QLCDNumber(self.timeBar)
        self.timeDisplay.setSegmentStyle(QLCDNumber.Flat)
        self.timeDisplay.setDigitCount(8)
        self.timeDisplay.display('00:00:00')
        self.timeDisplay.enterEvent = self.enterEvent

        def countbar_resize(event):
            self.timeDisplay.resize(event.size())

        self.timeBar.resizeEvent = countbar_resize

        self.status_icon = QLabel(self)
        self.status_icon.setPixmap(self.STOPPED.pixmap(12, 12))

    def set_cue(self, cue):
        super().set_cue(cue)

        queued = Connection.QtQueued

        # Media status changed
        self.cue.media.interrupted.connect(self._status_stopped, mode=queued)
        self.cue.media.interrupted.connect(self.dbmeter.reset, mode=queued)
        self.cue.media.stopped.connect(self._status_stopped, mode=queued)
        self.cue.media.stopped.connect(self.dbmeter.reset, mode=queued)
        self.cue.media.played.connect(self._status_playing, mode=queued)
        self.cue.media.paused.connect(self._status_paused, mode=queued)
        self.cue.media.error.connect(self._status_error, mode=queued)
        # self.cue.media.waiting.connect(self._status_paused)
        self.cue.media.eos.connect(self._status_stopped, mode=queued)
        self.cue.media.eos.connect(self.dbmeter.reset, mode=queued)
        self.cue.media.error.connect(self._on_error, mode=queued)
        self.cue.media.error.connect(self.dbmeter.reset, mode=queued)
        self.cue.media.property_changed.connect(self._media_changed,
                                                mode=queued)

        self.media_time = MediaTime(self.cue.media)
        self.media_time.notify.connect(self._on_time_update)

        self.seekSlider.sliderMoved.connect(self.cue.media.seek)
        self.seekSlider.sliderJumped.connect(self.cue.media.seek)

        self._update_duration(self.cue.media.duration)

    def select(self):
        self.selected = not self.selected
        self.update_style()

    def set_countdown_mode(self, mode):
        self._countdown_mode = mode
        self._on_time_update(self.cue.media.current_time())

    def set_accurate_timing(self, enable):
        self._accurate_timing = enable
        if self.cue.media.current_time() != -1:
            self._on_time_update(self.cue.media.current_time(), True)
        else:
            self._on_time_update(self.cue.media.duration, True)

    def show_dbmeters(self, visible):
        if self._dbmeter_element is not None:
            self._dbmeter_element.level_ready.disconnect(self.dbmeter.plot)
            self._dbmeter_element = None

        if visible:
            self._dbmeter_element = self.cue.media.element("DbMeter")
            if self._dbmeter_element is not None:
                self._dbmeter_element.level_ready.connect(self.dbmeter.plot)

        self._show_dbmeter = visible
        self.dbmeter.setVisible(visible)
        self.update()

    def cue_updated(self):
        super().cue_updated()
        self.show_dbmeters(self._show_dbmeter)

        new_fade = self.cue.media.element("Fade")
        if new_fade is not self.fade:
            if self.fade is not None:
                self.fade.enter_fadein.disconnect(self._enter_fadein)
                self.fade.enter_fadeout.disconnect(self._enter_fadeout)
                self.fade.exit_fadein.disconnect(self._exit_fade)
                self.fade.exit_fadeout.disconnect(self._exit_fade)

            if new_fade is not None:
                self.fade = new_fade
                self.fade.enter_fadein.connect(self._enter_fadein)
                self.fade.enter_fadeout.connect(self._enter_fadeout)
                self.fade.exit_fadein.connect(self._exit_fade)
                self.fade.exit_fadeout.connect(self._exit_fade)

    def _media_changed(self, pname, value):
        if pname == 'duration':
            self._update_duration(value)

    def _on_error(self, media, error, details):
        QDetailedMessageBox.dcritical(self.cue["name"], error, details)

    def _enter_fadein(self):
        p = self.timeDisplay.palette()
        p.setColor(p.WindowText, QColor(0, 255, 0))
        self.timeDisplay.setPalette(p)

    def _enter_fadeout(self):
        p = self.timeDisplay.palette()
        p.setColor(p.WindowText, QColor(255, 50, 50))
        self.timeDisplay.setPalette(p)

    def _exit_fade(self):
        self.timeDisplay.setPalette(self.timeBar.palette())

    def _status_stopped(self):
        self.status_icon.setPixmap(self.STOPPED.pixmap(12, 12))

    def _status_playing(self):
        self.status_icon.setPixmap(self.PLAYING.pixmap(12, 12))

    def _status_paused(self):
        self.status_icon.setPixmap(self.PAUSED.pixmap(12, 12))

    def _status_error(self):
        self.status_icon.setPixmap(self.ERROR.pixmap(12, 12))

    def _update_duration(self, duration):
        # Update the maximum values of seek-slider and time progress-bar
        self.seekSlider.setMaximum(duration)
        if duration > 0:
            self.timeBar.setMaximum(duration)
        else:
            self.timeBar.setMaximum(1)
            self.timeBar.setValue(1)

        # If not in playing or paused update the widget showed time
        state = self.cue.media.state
        if state != MediaState.Playing or state != MediaState.Paused:
            self._on_time_update(duration, True)

    def _on_time_update(self, time, ignore_visibility=False):
        if ignore_visibility or not self.visibleRegion().isEmpty():
            # If the given value is the duration or < 0 set the time to 0
            if time == self.cue.media.duration or time < 0:
                time = 0

            # Set the value the seek slider
            self.seekSlider.setValue(time)

            # If in count-down mode the widget will show the remaining time
            if self._countdown_mode:
                time = self.cue.media.duration - time

            # Set the value of the timer progress-bar
            if self.cue.media.duration > 0:
                self.timeBar.setValue(time)

            # Show the time in the widget
            self.timeDisplay.display(strtime(time,
                                             accurate=self._accurate_timing))

    def update(self):
        super().update()

        xdim = self.geometry().width()
        ydim = self.geometry().height() / 5
        ypos = self.geometry().height() - ydim
        self.timeBar.setGeometry(0, ypos, xdim, ydim)

        ydim2 = self.geometry().height() / 5
        ypos = self.geometry().height() - (ydim + ydim2)
        ydim = self.geometry().height() - ydim
        if self._show_dbmeter:
            xdim -= self.geometry().width() / 6

        self.nameButton.setGeometry(0, 0, xdim, ydim - 1)
        self.seekSlider.setGeometry(0, ypos, xdim, ydim2 - 4)

        if self._show_dbmeter:
            xpos = xdim
            xdim = self.geometry().width() / 6
            self.dbmeter.setGeometry(xpos + 2, 0, xdim - 4, ydim)

        self.status_icon.setGeometry(4, 4, 12, 12)
