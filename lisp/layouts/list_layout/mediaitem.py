##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import *  # @UnusedWildImport

from lisp.core.media_time import MediaTime
from lisp.ui.qmessagebox import QDetailedMessageBox
from lisp.utils.util import strtime


class MediaItem(QTreeWidgetItem):

    UNDERLINE_CSS = 'text-decoration: underline;'

    PLAY = QIcon.fromTheme("media-playback-start")
    PAUSE = QIcon.fromTheme("media-playback-pause")
    ERROR = QIcon.fromTheme("dialog-error")

    def __init__(self, cue, view, **kwds):
        super().__init__(**kwds)

        self.cue = cue
        self.media = cue.media
        self.view = view
        self.selected = False
        self._accurate_time = False

        self.actionsList = []
        self.actionIndex = -1

        self.init()

        self.media_time = MediaTime(self.cue.media)
        self.media_time.notify.connect(self.update_time)

        self.cue.updated.connect(self.update_item)

        self.media.duration.connect(self.update_duration)
        self.media.on_play.connect(self.on_play)
        self.media.on_stop.connect(self.reset_status)
        self.media.on_pause.connect(self.on_pause)
        self.media.interrupted.connect(self.reset_status)
        self.media.eos.connect(self.reset_status)
        self.media.error.connect(self.on_error)

        self.update_item()
        self.update_duration()

    def init(self):
        self.status = QLabel(self.view)
        self.status.setStyleSheet('background: transparent;'
                                  'padding-left: 20px;')
        self.view.setItemWidget(self, 0, self.status)

        self.timeProgress = QProgressBar(self.view)
        self.timeProgress.setStyleSheet('background: transparent;'
                                        'border-color: rgb(28, 66, 111);'
                                        'margin: 2px;')

        self.setTextAlignment(2, QtCore.Qt.AlignCenter)
        self.update_duration()

        def sizeHint():
            size = self.sizeHint(3)
            size.setHeight(size.height() - 4)
            size.setWidth(size.width() - 4)
            return size
        self.timeProgress.sizeHint = sizeHint
        self.view.setItemWidget(self, 3, self.timeProgress)
        self.timeProgress.setValue(0)
        self.timeProgress.setFormat('00:00:00')

    def select(self):
        self.selected = not self.selected
        if self.selected:
            self.setIcon(0, QIcon.fromTheme("media-record"))
        else:
            self.setIcon(0, QIcon())

    def set_accurate_time(self, enable):
        self._accurate_time = enable
        self.update_duration()

    def update_duration(self):
        self.setText(2, strtime(self.media['duration'],
                                accurate=self._accurate_time))
        self.timeProgress.setMaximum(self.media['duration'])

    def update_item(self):
        self.setText(1, self.cue['name'])

    def update_time(self, time):
        # If the given value is the duration or < 0 set the time to 0
        if time == self.cue.media['duration'] or time < 0:
            time = 0
        # Set the progress-bar value
        self.timeProgress.setValue(time)
        # Show the time in the widget
        self.timeProgress.setFormat(strtime(time,
                                            accurate=self._accurate_time))

    def on_play(self):
        self.status.setPixmap(self.PLAY.pixmap(16, 16))

    def on_pause(self):
        self.status.setPixmap(self.PAUSE.pixmap(16, 16))

    def on_error(self, media, error, details):
        self.status.setPixmap(self.ERROR.pixmap(16, 16))
        QDetailedMessageBox.dcritical(self.cue["name"], error, details)

    def reset_status(self):
        self.status.setPixmap(QPixmap())
