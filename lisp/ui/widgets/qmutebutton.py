# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtWidgets import QPushButton

from lisp.ui.icons import IconTheme


class QMuteButton(QPushButton):
    def __init__(self, *args):
        super().__init__(*args)

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
            self.setIcon(IconTheme.get("audio-volume-muted"))
        else:
            self.setIcon(IconTheme.get("audio-volume-high"))
