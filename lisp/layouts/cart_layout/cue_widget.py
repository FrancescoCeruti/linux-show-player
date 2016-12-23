# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QPoint
from PyQt5.QtGui import QColor, QDrag
from PyQt5.QtWidgets import QProgressBar, QLCDNumber, QLabel, QHBoxLayout, \
    QWidget, QGridLayout, QSizePolicy

from lisp.backend.audio_utils import slider_to_fader, fader_to_slider
from lisp.core.signal import Connection
from lisp.core.util import strtime
from lisp.cues.cue import CueState
from lisp.cues.cue_time import CueTime
from lisp.cues.media_cue import MediaCue
from lisp.layouts.cart_layout.page_widget import PageWidget
from lisp.ui.ui_utils import pixmap_from_icon
from lisp.ui.widgets import QClickLabel, QClickSlider, QDbMeter,\
    QDetailedMessageBox


class CueWidget(QWidget):
    ICON_SIZE = 14
    SLIDER_RANGE = 1000

    context_menu_request = pyqtSignal(object, QPoint)
    edit_request = pyqtSignal(object)
    cue_executed = pyqtSignal(object)

    def __init__(self, cue, **kwargs):
        super().__init__(**kwargs)
        self.cue = None

        self._selected = False
        self._accurate_timing = False
        self._show_dbmeter = False
        self._show_volume = False
        self._countdown_mode = True

        self._dbmeter_element = None
        self._fade_element = None
        self._volume_element = None

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setLayout(QGridLayout())

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(2)
        self.layout().setColumnStretch(0, 6)
        self.layout().setRowStretch(0, 4)

        self.nameButton = QClickLabel(self)
        self.nameButton.setObjectName('ButtonCueWidget')
        self.nameButton.setWordWrap(True)
        self.nameButton.setAlignment(Qt.AlignCenter)
        self.nameButton.setFocusPolicy(Qt.NoFocus)
        self.nameButton.clicked.connect(self._clicked)
        self.nameButton.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.layout().addWidget(self.nameButton, 0, 0)

        self.statusIcon = QLabel(self.nameButton)
        self.statusIcon.setStyleSheet('background-color: transparent')
        self.statusIcon.setPixmap(
            pixmap_from_icon('led-off', CueWidget.ICON_SIZE))

        self.seekSlider = QClickSlider(self.nameButton)
        self.seekSlider.setOrientation(Qt.Horizontal)
        self.seekSlider.setFocusPolicy(Qt.NoFocus)
        self.seekSlider.setVisible(False)

        self.volumeSlider = QClickSlider(self.nameButton)
        self.volumeSlider.setObjectName('VolumeSlider')
        self.volumeSlider.setOrientation(Qt.Vertical)
        self.volumeSlider.setFocusPolicy(Qt.NoFocus)
        self.volumeSlider.setRange(0, CueWidget.SLIDER_RANGE)
        self.volumeSlider.setPageStep(10)
        self.volumeSlider.valueChanged.connect(
            self._change_volume, Qt.DirectConnection)
        self.volumeSlider.setVisible(False)

        self.dbMeter = QDbMeter(self)
        self.dbMeter.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.dbMeter.setVisible(False)

        self.timeBar = QProgressBar(self)
        self.timeBar.setTextVisible(False)
        self.timeBar.setLayout(QHBoxLayout())
        self.timeBar.layout().setContentsMargins(0, 0, 0, 0)
        self.timeDisplay = QLCDNumber(self.timeBar)
        self.timeDisplay.setStyleSheet('background-color: transparent')
        self.timeDisplay.setSegmentStyle(QLCDNumber.Flat)
        self.timeDisplay.setDigitCount(8)
        self.timeDisplay.display('00:00:00')
        self.timeBar.layout().addWidget(self.timeDisplay)
        self.timeBar.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.timeBar.setVisible(False)

        self._set_cue(cue)

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value
        self._update_style(self.cue.stylesheet)

    def contextMenuEvent(self, event):
        self.context_menu_request.emit(self, event.globalPos())

    def mouseMoveEvent(self, event):
        if (event.buttons() == Qt.LeftButton and
                (event.modifiers() == Qt.ControlModifier or
                         event.modifiers() == Qt.ShiftModifier)):
            mime_data = QMimeData()
            mime_data.setText(PageWidget.DRAG_MAGIC)

            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setPixmap(self.grab(self.rect()))

            if event.modifiers() == Qt.ControlModifier:
                drag.exec_(Qt.MoveAction)
            else:
                drag.exec_(Qt.CopyAction)

            event.accept()
        else:
            event.ignore()

    def set_countdown_mode(self, mode):
        self._countdown_mode = mode
        self._update_time(self.cue.current_time())

    def set_accurate_timing(self, enable):
        self._accurate_timing = enable
        if self.cue.state & CueState.Pause:
            self._update_time(self.cue.current_time(), True)
        elif not self.cue.state & CueState.Running:
            self._update_duration(self.cue.duration)

    def show_seek_slider(self, visible):
        if isinstance(self.cue, MediaCue):
            self.seekSlider.setVisible(visible)
            self.update()

    def show_dbmeters(self, visible):
        if isinstance(self.cue, MediaCue):
            self._show_dbmeter = visible

            if self._dbmeter_element is not None:
                self._dbmeter_element.level_ready.disconnect(self.dbMeter.plot)
                self._dbmeter_element = None

            if visible:
                self._dbmeter_element = self.cue.media.element('DbMeter')
                if self._dbmeter_element is not None:
                    self._dbmeter_element.level_ready.connect(self.dbMeter.plot)

                self.layout().addWidget(self.dbMeter, 0, 2)
                self.layout().setColumnStretch(2, 1)
                self.dbMeter.show()
            else:
                self.layout().removeWidget(self.dbMeter)
                self.layout().setColumnStretch(2, 0)
                self.dbMeter.hide()

            self.update()

    def show_volume_slider(self, visible):
        if isinstance(self.cue, MediaCue):
            self._show_volume = visible

            if self._volume_element is not None:
                self._volume_element.changed('volume').disconnect(
                    self.reset_volume)
                self._volume_element = None

            if visible:
                self.volumeSlider.setEnabled(self.cue.state & CueState.Running)
                self._volume_element = self.cue.media.element('Volume')
                if self._volume_element is not None:
                    self.reset_volume()
                    self._volume_element.changed('volume').connect(
                        self.reset_volume,
                        Connection.QtQueued)

                self.layout().addWidget(self.volumeSlider, 0, 1)
                self.layout().setColumnStretch(1, 1)
                self.volumeSlider.show()
            else:
                self.layout().removeWidget(self.volumeSlider)
                self.layout().setColumnStretch(1, 0)
                self.volumeSlider.hide()

            self.update()

    def reset_volume(self):
        if self._volume_element is not None:
            self.volumeSlider.setValue(round(fader_to_slider(
                self._volume_element.volume) * CueWidget.SLIDER_RANGE))

    def _set_cue(self, cue):
        self.cue = cue

        # Cue properties changes
        self.cue.changed('name').connect(
            self._update_name, Connection.QtQueued)
        self.cue.changed('stylesheet').connect(
            self._update_style, Connection.QtQueued)
        self.cue.changed('duration').connect(
            self._update_duration, Connection.QtQueued)
        self.cue.changed('description').connect(
            self._update_description, Connection.QtQueued)

        # Fade enter/exit
        self.cue.fadein_start.connect(self._enter_fadein, Connection.QtQueued)
        self.cue.fadein_end.connect(self._exit_fade, Connection.QtQueued)
        self.cue.fadeout_start.connect(self._enter_fadeout, Connection.QtQueued)
        self.cue.fadeout_end.connect(self._exit_fade, Connection.QtQueued)

        # Cue status changed
        self.cue.interrupted.connect(self._status_stopped, Connection.QtQueued)
        self.cue.started.connect(self._status_playing, Connection.QtQueued)
        self.cue.stopped.connect(self._status_stopped, Connection.QtQueued)
        self.cue.paused.connect(self._status_paused, Connection.QtQueued)
        self.cue.error.connect(self._status_error, Connection.QtQueued)
        self.cue.end.connect(self._status_stopped, Connection.QtQueued)

        # DbMeter connections
        if isinstance(cue, MediaCue):
            self.cue.media.elements_changed.connect(
                self._media_updated, Connection.QtQueued)

            self.cue.paused.connect(self.dbMeter.reset, Connection.QtQueued)
            self.cue.stopped.connect(self.dbMeter.reset, Connection.QtQueued)
            self.cue.end.connect(self.dbMeter.reset, Connection.QtQueued)
            self.cue.error.connect(self.dbMeter.reset, Connection.QtQueued)

            self.seekSlider.sliderMoved.connect(self.cue.media.seek)
            self.seekSlider.sliderJumped.connect(self.cue.media.seek)

        self._cue_time = CueTime(self.cue)
        self._cue_time.notify.connect(self._update_time, Connection.QtQueued)

        self._update_name(cue.name)
        self._update_style(cue.stylesheet)
        self._update_duration(self.cue.duration)

    def _media_updated(self):
        self.show_dbmeters(self._show_dbmeter)
        self.show_volume_slider(self._show_volume)

    def _update_name(self, name):
        self.nameButton.setText(name)

    def _update_description(self, description):
        self.nameButton.setToolTip(description)

    def _change_volume(self, new_volume):
        self._volume_element.current_volume = slider_to_fader(
            new_volume / CueWidget.SLIDER_RANGE)

    def _clicked(self, event):
        if not (self.seekSlider.geometry().contains(event.pos()) and
                    self.seekSlider.isVisible()):
            if event.button() != Qt.RightButton:
                if event.modifiers() == Qt.ShiftModifier:
                    self.edit_request.emit(self.cue)
                elif event.modifiers() == Qt.ControlModifier:
                    self.selected = not self.selected
                else:
                    self.cue_executed.emit(self.cue)
                    self.cue.execute()

    def _update_style(self, stylesheet):
        stylesheet += 'text-decoration: underline;' if self.selected else ''
        self.nameButton.setStyleSheet(stylesheet)

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
        self.statusIcon.setPixmap(
            pixmap_from_icon('led-off', CueWidget.ICON_SIZE))
        self.volumeSlider.setEnabled(False)
        self._update_time(0, True)
        self.reset_volume()

    def _status_playing(self):
        self.statusIcon.setPixmap(
            pixmap_from_icon('led-running', CueWidget.ICON_SIZE))
        self.volumeSlider.setEnabled(True)

    def _status_paused(self):
        self.statusIcon.setPixmap(
            pixmap_from_icon('led-pause', CueWidget.ICON_SIZE))
        self.volumeSlider.setEnabled(False)

    def _status_error(self, cue, error, details):
        self.statusIcon.setPixmap(
            pixmap_from_icon('led-error', CueWidget.ICON_SIZE))
        self.volumeSlider.setEnabled(False)
        self.reset_volume()

        QDetailedMessageBox.dcritical(self.cue.name, error, details)

    def _update_duration(self, duration):
        # Update the maximum values of seek-slider and time progress-bar
        if duration > 0:
            if not self.timeBar.isVisible():
                self.layout().addWidget(self.timeBar, 1, 0, 1, 3)
                self.layout().setRowStretch(1, 1)
                self.timeBar.show()
            self.timeBar.setMaximum(duration)
            self.seekSlider.setMaximum(duration)
        else:
            self.timeBar.hide()
            self.layout().setRowStretch(1, 0)

        if not self.cue.state & CueState.Running:
            self._update_time(duration, True)

    def _update_time(self, time, ignore_visibility=False):
        if ignore_visibility or not self.visibleRegion().isEmpty():
            # If the given value is the duration or < 0 set the time to 0
            if time == self.cue.duration or time < 0:
                time = 0

            # Set the value the seek slider
            self.seekSlider.setValue(time)

            # If in count-down mode the widget will show the remaining time
            if self._countdown_mode:
                time = self.cue.duration - time

            # Set the value of the timer progress-bar
            if self.cue.duration > 0:
                self.timeBar.setValue(time)

            # Show the time in the widget
            self.timeDisplay.display(
                strtime(time, accurate=self._accurate_timing))

    def resizeEvent(self, event):
        self.update()

    def update(self):
        super().update()
        self.layout().activate()

        s_width = self.nameButton.width() - 8
        s_height = self.seekSlider.height()
        s_ypos = self.nameButton.height() - s_height

        self.seekSlider.setGeometry(4, s_ypos, s_width, s_height)
        self.statusIcon.setGeometry(4, 4,
                                    CueWidget.ICON_SIZE,
                                    CueWidget.ICON_SIZE)
