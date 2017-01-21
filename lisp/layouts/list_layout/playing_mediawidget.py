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

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QSizePolicy, \
    QPushButton, QLCDNumber

from lisp.core.configuration import config
from lisp.core.fade_functions import FadeOutType, FadeInType
from lisp.core.signal import Connection
from lisp.core.util import strtime
from lisp.cues.cue_time import CueTime
from lisp.layouts.list_layout.control_buttons import CueControlButtons
from lisp.ui.widgets import QClickSlider, QDbMeter


class PlayingMediaWidget(QWidget):

    def __init__(self, cue, **kwargs):
        super().__init__(**kwargs)
        self.setFocusPolicy(Qt.NoFocus)
        self.setGeometry(0, 0, self.parent().viewport().width(), 110)

        self.cue = cue
        self.cue_time = CueTime(cue)
        self.cue_time.notify.connect(self._time_updated, Connection.QtQueued)

        self._dbmeter_element = None
        self._accurate_time = False

        self.gridLayoutWidget = QWidget(self)
        self.gridLayoutWidget.setGeometry(self.geometry())
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(3, 3, 3, 3)
        self.gridLayout.setSpacing(2)

        self.nameLabel = QLabel(self.gridLayoutWidget)
        self.nameLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.nameLabel.setText(cue.name)
        self.nameLabel.setToolTip(cue.name)
        self.gridLayout.addWidget(self.nameLabel, 0, 0, 1, 2)

        self.controlButtons = CueControlButtons(parent=self.gridLayoutWidget)
        self.controlButtons.stopButton.clicked.connect(self._stop)
        self.controlButtons.pauseButton.clicked.connect(self._pause)
        self.controlButtons.startButton.clicked.connect(self._start)
        self.controlButtons.fadeInButton.clicked.connect(self._fadein)
        self.controlButtons.fadeOutButton.clicked.connect(self._fadeout)
        self.controlButtons.interruptButton.clicked.connect(self._interrupt)
        self.gridLayout.addWidget(self.controlButtons, 1, 0)

        self.timeDisplay = QLCDNumber(self.gridLayoutWidget)
        self.timeDisplay.setStyleSheet('background-color: transparent')
        self.timeDisplay.setSegmentStyle(QLCDNumber.Flat)
        self.timeDisplay.setDigitCount(8)
        self.timeDisplay.display(strtime(cue.media.duration))
        self.gridLayout.addWidget(self.timeDisplay, 1, 1)

        self.seekSlider = QClickSlider(self.gridLayoutWidget)
        self.seekSlider.setOrientation(Qt.Horizontal)
        self.seekSlider.setRange(0, cue.media.duration)
        self.seekSlider.setFocusPolicy(Qt.NoFocus)
        self.seekSlider.sliderMoved.connect(self._seek)
        self.seekSlider.sliderJumped.connect(self._seek)
        self.seekSlider.setVisible(False)

        self.dbmeter = QDbMeter(self.gridLayoutWidget)
        self.dbmeter.setVisible(False)

        self.gridLayout.setRowStretch(0, 1)
        self.gridLayout.setRowStretch(1, 3)
        self.gridLayout.setColumnStretch(0, 7)
        self.gridLayout.setColumnStretch(1, 5)

        cue.changed('name').connect(self.name_changed)
        cue.changed('duration').connect(self.update_duration)
        cue.started.connect(self.controlButtons.pauseMode)
        cue.paused.connect(self.controlButtons.startMode)

        # Fade enter/exit
        cue.fadein_start.connect(self.enter_fadein, Connection.QtQueued)
        cue.fadein_end.connect(self.exit_fade, Connection.QtQueued)
        cue.fadeout_start.connect(self.enter_fadeout, Connection.QtQueued)
        cue.fadeout_end.connect(self.exit_fade, Connection.QtQueued)

    def enter_fadein(self):
        p = self.timeDisplay.palette()
        p.setColor(p.Text, QColor(0, 255, 0))
        self.timeDisplay.setPalette(p)

    def enter_fadeout(self):
        p = self.timeDisplay.palette()
        p.setColor(p.Text, QColor(255, 50, 50))
        self.timeDisplay.setPalette(p)

    def exit_fade(self):
        self.timeDisplay.setPalette(self.palette())

    def name_changed(self, name):
        self.nameLabel.setText(name)
        self.nameLabel.setToolTip(name)

    def set_accurate_time(self, enable):
        self._accurate_time = enable

    def set_seek_visible(self, visible):
        if visible and not self.seekSlider.isVisible():
            self.gridLayout.addWidget(self.seekSlider, 2, 0, 1, 2)
            self.gridLayout.setRowStretch(2, 1)
        elif not visible and self.seekSlider.isVisible():
            self.gridLayout.removeWidget(self.seekSlider)
            self.gridLayout.setRowStretch(2, 0)

        self.seekSlider.setVisible(visible)

    def set_dbmeter_visible(self, visible):
        if self._dbmeter_element is not None:
            self._dbmeter_element.level_ready.disconnect(self.dbmeter.plot)
            self._dbmeter_element = None

        if visible:
            self._dbmeter_element = self.cue.media.element('DbMeter')
            if self._dbmeter_element is not None:
                self._dbmeter_element.level_ready.connect(self.dbmeter.plot)

        # Add/Remove the QDbMeter in the layout
        if visible and not self.dbmeter.isVisible():
            self.gridLayout.addWidget(self.dbmeter, 0, 2, 3, 1)
            self.gridLayout.setColumnStretch(2, 1)
        elif not visible and self.dbmeter.isVisible():
            self.gridLayout.removeWidget(self.dbmeter)
            self.gridLayout.setColumnStretch(2, 0)

        self.dbmeter.setVisible(visible)

    def _time_updated(self, time):
        if not self.visibleRegion().isEmpty():
            # If the given value is the duration or < 0 set the time to 0
            if time == self.cue.media.duration or time < 0:
                time = 0

            # Set the value the seek slider
            self.seekSlider.setValue(time)

            # Show the time in the widget
            self.timeDisplay.display(strtime(self.cue.media.duration - time,
                                             accurate=self._accurate_time))

    def update_duration(self, duration):
        self.seekSlider.setMaximum(duration)

    def _pause(self):
        self.cue.pause(fade=config['ListLayout'].getboolean('PauseCueFade'))

    def _start(self):
        self.cue.start(fade=config['ListLayout'].getboolean('RestartCueFade'))

    def _stop(self):
        self.cue.stop(fade=config['ListLayout'].getboolean('StopCueFade'))

    def _interrupt(self):
        self.cue.interrupt(
            fade=config['ListLayout'].getboolean('InterruptCueFade'))

    def _fadeout(self):
        self.cue.fadeout(config['ListLayout'].getfloat('CueFadeDuration'),
                         FadeOutType[config['ListLayout'].get('CueFadeType')])

    def _fadein(self):
        self.cue.fadein(config['ListLayout'].getfloat('CueFadeDuration'),
                        FadeInType[config['ListLayout'].get('CueFadeType')])

    def _seek(self, position):
        self.cue.media.seek(position)
