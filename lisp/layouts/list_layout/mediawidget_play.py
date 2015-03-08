##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QSizePolicy, \
    QPushButton, QLCDNumber
from lisp.ui.qclickslider import QClickSlider

from lisp.ui.qdbmeter import QDbMeter
from lisp.utils.util import strtime


class PlayingMediaWidget(QWidget):

    def __init__(self, cue, media_time, parent=None):
        super().__init__(parent)

        self.cue = cue
        self.media_time = media_time

        self._dbmeter_element = None
        self._accurate_time = False

        scroll_size = (self.parent().verticalScrollBar().width() + 5)
        self.setGeometry(0, 0, self.parent().width() - scroll_size, 102)
        self.setFocusPolicy(Qt.NoFocus)

        self.gridLayoutWidget = QWidget(self)
        self.gridLayoutWidget.setGeometry(self.geometry())
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(2, 2, 2, 2)

        self.nameLabel = QLabel(self.gridLayoutWidget)
        self.nameLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.nameLabel.setText(cue['name'])
        self.nameLabel.setToolTip(cue['name'])
        self.gridLayout.addWidget(self.nameLabel, 0, 0, 1, 3)

        self.playPauseButton = QPushButton(self.gridLayoutWidget)
        self.playPauseButton.setSizePolicy(QSizePolicy.Ignored,
                                           QSizePolicy.Ignored)
        self.playPauseButton.setIcon(QIcon.fromTheme("media-playback-pause"))
        self.playPauseButton.setFocusPolicy(Qt.NoFocus)
        self.playPauseButton.clicked.connect(lambda: self.cue.media.pause())
        self.gridLayout.addWidget(self.playPauseButton, 1, 0)

        self.stopButton = QPushButton(self.gridLayoutWidget)
        self.stopButton.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.stopButton.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.stopButton.setFocusPolicy(Qt.NoFocus)
        self.stopButton.clicked.connect(lambda m: cue.media.stop())
        self.gridLayout.addWidget(self.stopButton, 1, 1)

        self.timeDisplay = QLCDNumber(self.gridLayoutWidget)
        self.timeDisplay.setSegmentStyle(QLCDNumber.Flat)
        self.timeDisplay.setDigitCount(8)
        self.timeDisplay.display(strtime(cue.media['duration']))
        self.gridLayout.addWidget(self.timeDisplay, 1, 2)

        self.seekSlider = QClickSlider(self.gridLayoutWidget)
        self.seekSlider.setOrientation(Qt.Horizontal)
        self.seekSlider.setRange(0, cue.media['duration'])
        self.seekSlider.setFocusPolicy(Qt.NoFocus)
        self.seekSlider.sliderMoved.connect(cue.media.seek)
        self.seekSlider.sliderJumped.connect(cue.media.seek)
        self.seekSlider.setVisible(False)

        self.dbmeter = QDbMeter(self.gridLayoutWidget)
        self.dbmeter.setVisible(False)

        self.gridLayout.setRowStretch(0, 1)
        self.gridLayout.setRowStretch(1, 2)
        self.gridLayout.setColumnStretch(0, 3)
        self.gridLayout.setColumnStretch(1, 3)
        self.gridLayout.setColumnStretch(2, 5)

        self.media_time.notify.connect(self.on_time_updated)

        cue.updated.connect(self.on_cue_updated)
        cue.media.duration.connect(self.update_duration)
        cue.media.played.connect(self._pause_to_play)
        cue.media.paused.connect(self._play_to_pause)

        self.fade = self.cue.media.element("Fade")
        if self.fade is not None:
            self.fade.enter_fadein.connect(self.enter_fadein)
            self.fade.enter_fadeout.connect(self.enter_fadeout)
            self.fade.exit_fadein.connect(self.exit_fade)
            self.fade.exit_fadeout.connect(self.exit_fade)

    def enter_fadeout(self):
        p = self.timeDisplay.palette()
        p.setColor(p.Text, QColor(255, 50, 50))
        self.timeDisplay.setPalette(p)

    def enter_fadein(self):
        p = self.timeDisplay.palette()
        p.setColor(p.Text, QColor(0, 255, 0))
        self.timeDisplay.setPalette(p)

    def exit_fade(self):
        self.timeDisplay.setPalette(self.palette())

    def on_cue_updated(self, cue):
        self.nameLabel.setText(cue['name'])
        self.nameLabel.setToolTip(cue['name'])

    def set_accurate_time(self, enable):
        self._accurate_time = enable

    def set_seek_visible(self, visible):
        if visible and not self.seekSlider.isVisible():
            self.gridLayout.addWidget(self.seekSlider, 2, 0, 1, 3)
            self.gridLayout.setRowStretch(2, 1)
        elif not visible and self.seekSlider.isVisible():
            self.gridLayout.removeWidget(self.seekSlider)
            self.gridLayout.setRowStretch(2, 0)

        self.seekSlider.setVisible(visible)

    def set_dbmeter_visible(self, visible):
        if self._dbmeter_element is not None:
            self._dbmeter_element.levelReady.disconnect(self.dbmeter.plot)
            self._dbmeter_element = None

        if visible:
            self._dbmeter_element = self.cue.media.element("DbMeter")
            if self._dbmeter_element is not None:
                self._dbmeter_element.levelReady.connect(self.dbmeter.plot)

        # Add/Remove the QDbMeter in the layout
        if visible and not self.dbmeter.isVisible():
            self.gridLayout.addWidget(self.dbmeter, 0, 3, 4, 1)
            self.gridLayout.setColumnStretch(3, 1)
        elif not visible and self.dbmeter.isVisible():
            self.gridLayout.removeWidget(self.dbmeter)
            self.gridLayout.setColumnStretch(3, 0)

        self.dbmeter.setVisible(visible)

    def on_time_updated(self, time):
        if not self.visibleRegion().isEmpty():
            # If the given value is the duration or < 0 set the time to 0
            if time == self.cue.media['duration'] or time < 0:
                time = 0

            # Set the value the seek slider
            self.seekSlider.setValue(time)

            # If in count-down mode the widget will show the remaining time
            time = self.cue.media['duration'] - time

            # Show the time in the widget
            self.timeDisplay.display(strtime(time,
                                             accurate=self._accurate_time))

    def update_duration(self, media, duration):
        self.seekSlider.setMaximum(duration)

    def _play_to_pause(self):
        self.playPauseButton.clicked.disconnect()
        self.playPauseButton.clicked.connect(lambda: self.cue.media.play())
        self.playPauseButton.setIcon(QIcon.fromTheme("media-playback-start"))

    def _pause_to_play(self):
        self.playPauseButton.clicked.disconnect()
        self.playPauseButton.clicked.connect(lambda: self.cue.media.pause())
        self.playPauseButton.setIcon(QIcon.fromTheme("media-playback-pause"))

    def destroy_widget(self):
        self.hide()
        self.set_dbmeter_visible(False)
        self.media_time.notify.disconnect(self.on_time_updated)

        if self.fade is not None:
            self.fade.enter_fadein.disconnect(self.enter_fadein)
            self.fade.enter_fadeout.disconnect(self.enter_fadeout)
            self.fade.exit_fadein.disconnect(self.exit_fade)
            self.fade.exit_fadeout.disconnect(self.exit_fade)

        self.cue.media.duration.disconnect(self.update_duration)
        self.cue.updated.disconnect(self.on_cue_updated)
