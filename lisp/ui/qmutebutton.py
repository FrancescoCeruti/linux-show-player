##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton


class QMuteButton(QPushButton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Use the button-check behaviors as mute-unmute
        self.setCheckable(True)
        self.setChecked(False)
        # Set the icon
        self.onToggle()

        # More explicit names
        self.isMute = self.isChecked
        self.setMute = self.setChecked

        self.toggled.connect(self.onToggle)

    def onToggle(self):
        if self.isChecked():
            self.setIcon(QIcon.fromTheme('audio-volume-muted'))
        else:
            self.setIcon(QIcon.fromTheme('audio-volume-high'))
