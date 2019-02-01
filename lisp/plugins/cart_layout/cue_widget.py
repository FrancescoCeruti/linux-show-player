# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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
from PyQt5.QtWidgets import (
    QProgressBar,
    QLCDNumber,
    QLabel,
    QHBoxLayout,
    QWidget,
    QSizePolicy,
    QVBoxLayout,
)

from lisp.backend.audio_utils import slider_to_fader, fader_to_slider
from lisp.core.signal import Connection
from lisp.core.util import strtime
from lisp.cues.cue import CueState
from lisp.cues.cue_time import CueTime
from lisp.cues.media_cue import MediaCue
from lisp.plugins.cart_layout.page_widget import CartPageWidget
from lisp.ui.icons import IconTheme
from lisp.ui.widgets import QClickLabel, QClickSlider, QDbMeter


class CueWidget(QWidget):
    ICON_SIZE = 14
    SLIDER_RANGE = 1000

    contextMenuRequested = pyqtSignal(QPoint)
    editRequested = pyqtSignal(object)
    cueExecuted = pyqtSignal(object)

    def __init__(self, cue, **kwargs):
        super().__init__(**kwargs)
        self._cue = None
        self._selected = False
        self._accurateTiming = False
        self._countdownMode = True
        self._showDBMeter = False
        self._showVolume = False

        self._dBMeterElement = None
        self._volumeElement = None
        self._fadeElement = None

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setLayout(QVBoxLayout())

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(2)

        self.hLayout = QHBoxLayout()
        self.hLayout.setContentsMargins(0, 0, 0, 0)
        self.hLayout.setSpacing(2)
        self.layout().addLayout(self.hLayout, 4)

        self.nameButton = QClickLabel(self)
        self.nameButton.setObjectName("ButtonCueWidget")
        self.nameButton.setWordWrap(True)
        self.nameButton.setAlignment(Qt.AlignCenter)
        self.nameButton.setFocusPolicy(Qt.NoFocus)
        self.nameButton.clicked.connect(self._clicked)
        self.nameButton.setSizePolicy(
            QSizePolicy.Ignored, QSizePolicy.Preferred
        )
        self.hLayout.addWidget(self.nameButton, 5)

        self.statusIcon = QLabel(self.nameButton)
        self.statusIcon.setStyleSheet("background-color: transparent")
        self.statusIcon.setPixmap(
            IconTheme.get("led-off").pixmap(CueWidget.ICON_SIZE)
        )

        self.seekSlider = QClickSlider(self.nameButton)
        self.seekSlider.setOrientation(Qt.Horizontal)
        self.seekSlider.setFocusPolicy(Qt.NoFocus)
        self.seekSlider.setVisible(False)

        self.volumeSlider = QClickSlider(self.nameButton)
        self.volumeSlider.setObjectName("VolumeSlider")
        self.volumeSlider.setOrientation(Qt.Vertical)
        self.volumeSlider.setFocusPolicy(Qt.NoFocus)
        self.volumeSlider.setRange(0, CueWidget.SLIDER_RANGE)
        self.volumeSlider.setPageStep(10)
        self.volumeSlider.valueChanged.connect(
            self._changeVolume, Qt.DirectConnection
        )
        self.volumeSlider.setVisible(False)

        self.dbMeter = QDbMeter(self)
        self.dbMeter.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.dbMeter.setVisible(False)

        self.timeBar = QProgressBar(self)
        self.timeBar.setTextVisible(False)
        self.timeBar.setLayout(QHBoxLayout())
        self.timeBar.layout().setContentsMargins(0, 0, 0, 0)
        self.timeDisplay = QLCDNumber(self.timeBar)
        self.timeDisplay.setStyleSheet("background-color: transparent")
        self.timeDisplay.setSegmentStyle(QLCDNumber.Flat)
        self.timeDisplay.setDigitCount(8)
        self.timeDisplay.display("00:00:00")
        self.timeBar.layout().addWidget(self.timeDisplay)
        self.timeBar.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.timeBar.setVisible(False)

        self._setCue(cue)

    @property
    def cue(self):
        return self._cue

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value
        # Show the selection via stylesheet/qproperties
        self.nameButton.setProperty("selected", self.selected)
        self.nameButton.style().unpolish(self.nameButton)
        self.nameButton.style().polish(self.nameButton)

    def contextMenuEvent(self, event):
        self.contextMenuRequested.emit(event.globalPos())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and (
            event.modifiers() == Qt.ControlModifier
            or event.modifiers() == Qt.ShiftModifier
        ):
            mime_data = QMimeData()
            mime_data.setText(CartPageWidget.DRAG_MAGIC)

            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setPixmap(self.grab(self.rect()))

            if event.modifiers() == Qt.ControlModifier:
                drag.exec_(Qt.CopyAction)
            else:
                drag.exec_(Qt.MoveAction)

    def setCountdownMode(self, mode):
        self._countdownMode = mode
        self._updateTime(self._cue.current_time(), True)

    def showAccurateTiming(self, enable):
        self._accurateTiming = enable
        if self._cue.state & CueState.Pause:
            self._updateTime(self._cue.current_time(), True)
        elif not self._cue.state & CueState.Running:
            self._updateDuration(self._cue.duration)

    def showSeekSlider(self, visible):
        if isinstance(self._cue, MediaCue):
            self.seekSlider.setVisible(visible)
            self.update()

    def showDBMeters(self, visible):
        if isinstance(self._cue, MediaCue):
            self._showDBMeter = visible

            if self._dBMeterElement is not None:
                self._dBMeterElement.level_ready.disconnect(self.dbMeter.plot)
                self._dBMeterElement = None

            if visible:
                self._dBMeterElement = self._cue.media.element("DbMeter")
                if self._dBMeterElement is not None:
                    self._dBMeterElement.level_ready.connect(self.dbMeter.plot)

                self.hLayout.insertWidget(2, self.dbMeter, 1)
                self.dbMeter.show()
            else:
                self.hLayout.removeWidget(self.dbMeter)
                self.dbMeter.hide()

            self.update()

    def showVolumeSlider(self, visible):
        if isinstance(self._cue, MediaCue):
            self._showVolume = visible

            if self._volumeElement is not None:
                self._volumeElement.changed("volume").disconnect(
                    self.resetVolume
                )
                self._volumeElement = None

            if visible:
                self.volumeSlider.setEnabled(self._cue.state & CueState.Running)
                self._volumeElement = self._cue.media.element("Volume")
                if self._volumeElement is not None:
                    self.resetVolume()
                    self._volumeElement.changed("volume").connect(
                        self.resetVolume, Connection.QtQueued
                    )

                self.hLayout.insertWidget(1, self.volumeSlider, 1)
                self.volumeSlider.show()
            else:
                self.hLayout.removeWidget(self.volumeSlider)
                self.volumeSlider.hide()

            self.update()

    def resetVolume(self):
        if self._volumeElement is not None:
            self.volumeSlider.setValue(
                round(
                    fader_to_slider(self._volumeElement.volume)
                    * CueWidget.SLIDER_RANGE
                )
            )

    def _setCue(self, cue):
        self._cue = cue

        # Cue properties changes
        self._cue.changed("name").connect(self._updateName, Connection.QtQueued)
        self._cue.changed("stylesheet").connect(
            self._updateStyle, Connection.QtQueued
        )
        self._cue.changed("duration").connect(
            self._updateDuration, Connection.QtQueued
        )
        self._cue.changed("description").connect(
            self._updateDescription, Connection.QtQueued
        )

        # FadeOut start/end
        self._cue.fadein_start.connect(self._enterFadein, Connection.QtQueued)
        self._cue.fadein_end.connect(self._exitFade, Connection.QtQueued)

        # FadeIn start/end
        self._cue.fadeout_start.connect(self._enterFadeout, Connection.QtQueued)
        self._cue.fadeout_end.connect(self._exitFade, Connection.QtQueued)

        # Cue status changed
        self._cue.interrupted.connect(self._statusStopped, Connection.QtQueued)
        self._cue.started.connect(self._statusPlaying, Connection.QtQueued)
        self._cue.stopped.connect(self._statusStopped, Connection.QtQueued)
        self._cue.paused.connect(self._statusPaused, Connection.QtQueued)
        self._cue.error.connect(self._statusError, Connection.QtQueued)
        self._cue.end.connect(self._statusStopped, Connection.QtQueued)

        # Media cues features dBMeter and seekSlider
        if isinstance(cue, MediaCue):
            self._cue.media.elements_changed.connect(
                self._mediaUpdated, Connection.QtQueued
            )

            self._cue.paused.connect(self.dbMeter.reset, Connection.QtQueued)
            self._cue.stopped.connect(self.dbMeter.reset, Connection.QtQueued)
            self._cue.end.connect(self.dbMeter.reset, Connection.QtQueued)
            self._cue.error.connect(self.dbMeter.reset, Connection.QtQueued)

            self.seekSlider.sliderMoved.connect(self._cue.media.seek)
            self.seekSlider.sliderJumped.connect(self._cue.media.seek)

        self._cueTime = CueTime(self._cue)
        self._cueTime.notify.connect(self._updateTime, Connection.QtQueued)

        self._updateName(cue.name)
        self._updateStyle(cue.stylesheet)
        self._updateDuration(self._cue.duration)

    def _mediaUpdated(self):
        self.showDBMeters(self._showDBMeter)
        self.showVolumeSlider(self._showVolume)

    def _updateName(self, name):
        self.nameButton.setText(name)

    def _updateDescription(self, description):
        self.nameButton.setToolTip(description)

    def _changeVolume(self, new_volume):
        self._volumeElement.live_volume = slider_to_fader(
            new_volume / CueWidget.SLIDER_RANGE
        )

    def _clicked(self, event):
        if not (
            self.seekSlider.geometry().contains(event.pos())
            and self.seekSlider.isVisible()
        ):
            if event.button() != Qt.RightButton:
                if event.modifiers() == Qt.ShiftModifier:
                    self.editRequested.emit(self._cue)
                elif event.modifiers() == Qt.ControlModifier:
                    self.selected = not self.selected
                else:
                    self._cue.execute()
                    self.cueExecuted.emit(self._cue)

    def _updateStyle(self, stylesheet):
        self.nameButton.setStyleSheet(stylesheet)

    def _enterFadein(self):
        p = self.timeDisplay.palette()
        p.setColor(p.WindowText, QColor(0, 255, 0))
        self.timeDisplay.setPalette(p)

    def _enterFadeout(self):
        p = self.timeDisplay.palette()
        p.setColor(p.WindowText, QColor(255, 50, 50))
        self.timeDisplay.setPalette(p)

    def _exitFade(self):
        self.timeDisplay.setPalette(self.timeBar.palette())

    def _statusStopped(self):
        self.statusIcon.setPixmap(
            IconTheme.get("led-off").pixmap(CueWidget.ICON_SIZE)
        )
        self.volumeSlider.setEnabled(False)
        self._updateTime(0, True)
        self.resetVolume()

    def _statusPlaying(self):
        self.statusIcon.setPixmap(
            IconTheme.get("led-running").pixmap(CueWidget.ICON_SIZE)
        )
        self.volumeSlider.setEnabled(True)

    def _statusPaused(self):
        self.statusIcon.setPixmap(
            IconTheme.get("led-pause").pixmap(CueWidget.ICON_SIZE)
        )
        self.volumeSlider.setEnabled(False)

    def _statusError(self):
        self.statusIcon.setPixmap(
            IconTheme.get("led-error").pixmap(CueWidget.ICON_SIZE)
        )
        self.volumeSlider.setEnabled(False)
        self.resetVolume()

    def _updateDuration(self, duration):
        # Update the maximum values of seek-slider and time progress-bar
        if duration > 0:
            if not self.timeBar.isVisible():
                self.layout().addWidget(self.timeBar, 1)
                self.timeBar.show()
            self.timeBar.setMaximum(duration)
            self.seekSlider.setMaximum(duration)
        else:
            self.layout().removeWidget(self.timeBar)
            self.timeBar.hide()

        if not self._cue.state & CueState.Running:
            self._updateTime(duration, True)

    def _updateTime(self, time, ignore_visibility=False):
        if ignore_visibility or not self.visibleRegion().isEmpty():
            # If the given value is the duration or < 0 set the time to 0
            if time == self._cue.duration or time < 0:
                time = 0

            # Set the value the seek slider
            self.seekSlider.setValue(time)

            # If in count-down mode the widget will show the remaining time
            if self._countdownMode:
                time = self._cue.duration - time

            # Set the value of the timer progress-bar
            if self._cue.duration > 0:
                self.timeBar.setValue(time)

            # Show the time in the widget
            self.timeDisplay.display(
                strtime(time, accurate=self._accurateTiming)
            )

    def resizeEvent(self, event):
        self.update()

    def update(self):
        super().update()
        self.hLayout.activate()
        self.layout().activate()

        s_width = self.nameButton.width() - 8
        s_height = self.seekSlider.height()
        s_ypos = self.nameButton.height() - s_height

        self.seekSlider.setGeometry(4, s_ypos, s_width, s_height)
        self.statusIcon.setGeometry(
            4, 4, CueWidget.ICON_SIZE, CueWidget.ICON_SIZE
        )
