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

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget, QGridLayout, QSizePolicy

from lisp.ui.icons import IconTheme
from lisp.ui.ui_utils import translate
from lisp.ui.widgets.qiconpushbutton import QIconPushButton


class ShowControlButtons(QWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self.setLayout(QGridLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(5)

        # Row 0
        self.pauseButton = self.newButton(IconTheme.get("cue-pause"))
        self.layout().addWidget(self.pauseButton, 0, 0)

        self.stopButton = self.newButton(IconTheme.get("cue-stop"))
        self.layout().addWidget(self.stopButton, 0, 1)

        self.interruptButton = self.newButton(IconTheme.get("cue-interrupt"))
        self.layout().addWidget(self.interruptButton, 0, 2)

        # Row 1
        self.resumeButton = self.newButton(IconTheme.get("cue-start"))
        self.layout().addWidget(self.resumeButton, 1, 0)

        self.fadeOutButton = self.newButton(IconTheme.get("fadeout-generic"))
        self.layout().addWidget(self.fadeOutButton, 1, 1)

        self.fadeInButton = self.newButton(IconTheme.get("fadein-generic"))
        self.layout().addWidget(self.fadeInButton, 1, 2)

        self.retranslateUi()

    def retranslateUi(self):
        # Row 0
        self.pauseButton.setToolTip(translate("ListLayout", "Pause all"))
        self.stopButton.setToolTip(translate("ListLayout", "Stop all"))
        self.interruptButton.setToolTip(
            translate("ListLayout", "Interrupt all")
        )
        # Row 1
        self.resumeButton.setToolTip(translate("ListLayout", "Resume all"))
        self.fadeOutButton.setToolTip(translate("ListLayout", "Fade-Out all"))
        self.fadeInButton.setToolTip(translate("ListLayout", "Fade-In all"))

    def newButton(self, icon):
        button = QIconPushButton(self)
        button.setFocusPolicy(Qt.NoFocus)
        button.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)
        button.setIcon(icon)
        button.setIconSize(QSize(32, 32))
        return button


class CueControlButtons(QWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QGridLayout())
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.layout().setSpacing(2)

        # Start/Pause
        self.pauseButton = self.newButton(IconTheme.get("cue-pause"))
        self.layout().addWidget(self.pauseButton, 0, 0, 2, 1)

        self.startButton = self.newButton(IconTheme.get("cue-start"))
        self.startButton.hide()

        # Row 0
        self.stopButton = self.newButton(IconTheme.get("cue-stop"))
        self.layout().addWidget(self.stopButton, 0, 1)

        self.interruptButton = self.newButton(IconTheme.get("cue-interrupt"))
        self.layout().addWidget(self.interruptButton, 0, 2)

        # Row 1
        self.fadeOutButton = self.newButton(IconTheme.get("fadeout-generic"))
        self.layout().addWidget(self.fadeOutButton, 1, 1)

        self.fadeInButton = self.newButton(IconTheme.get("fadein-generic"))
        self.layout().addWidget(self.fadeInButton, 1, 2)

        self.layout().setColumnStretch(0, 3)
        self.layout().setColumnStretch(1, 2)
        self.layout().setColumnStretch(2, 2)

    def pauseMode(self):
        self.layout().addWidget(self.pauseButton, 0, 0, 2, 1)
        self.pauseButton.show()
        self.startButton.hide()

    def startMode(self):
        self.layout().addWidget(self.startButton, 0, 0, 2, 1)
        self.startButton.show()
        self.pauseButton.hide()

    def newButton(self, icon):
        button = QIconPushButton(self)
        button.setFocusPolicy(Qt.NoFocus)
        button.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        button.setIcon(icon)
        button.setIconSize(QSize(32, 32))
        return button
