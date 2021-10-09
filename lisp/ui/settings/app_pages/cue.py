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

from PyQt5.QtCore import QT_TRANSLATE_NOOP, Qt
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QLabel

from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate
from lisp.ui.widgets import FadeEdit


class CueAppSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Cue Settings")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        # Interrupt fade settings
        self.interruptGroup = QGroupBox(self)
        self.interruptGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.interruptGroup)

        self.interruptHelpText = QLabel(self.interruptGroup)
        self.interruptHelpText.setWordWrap(True)
        self.interruptGroup.layout().addWidget(self.interruptHelpText)

        self.interruptFadeEdit = FadeEdit(self.interruptGroup)
        self.interruptGroup.layout().addWidget(self.interruptFadeEdit)

        # Fade action defaults
        self.fadeActionsDefaultsGroup = QGroupBox(self)
        self.fadeActionsDefaultsGroup.setLayout(QVBoxLayout())
        self.fadeActionsDefaultsGroup.layout().setSpacing(
            self.fadeActionsDefaultsGroup.layout().contentsMargins().top()
        )
        self.layout().addWidget(self.fadeActionsDefaultsGroup)

        self.fadeActionDefaultsHelpText = QLabel(self.fadeActionsDefaultsGroup)
        self.fadeActionDefaultsHelpText.setAlignment(Qt.AlignCenter)
        font = self.fadeActionDefaultsHelpText.font()
        font.setPointSizeF(font.pointSizeF() * 0.9)
        self.fadeActionDefaultsHelpText.setFont(font)
        self.fadeActionsDefaultsGroup.layout().addWidget(
            self.fadeActionDefaultsHelpText
        )

        self.fadeActionEdit = FadeEdit(self.fadeActionsDefaultsGroup)
        self.fadeActionsDefaultsGroup.layout().addWidget(self.fadeActionEdit)

        self.retranslateUi()

    def retranslateUi(self):
        self.interruptGroup.setTitle(
            translate("CueSettings", "Interrupt fade")
        )
        self.interruptHelpText.setText(
            translate(
                "CueSettings",
                "Used globally when interrupting cues",
            )
        )
        self.fadeActionsDefaultsGroup.setTitle(
            translate("CueSettings", "Fallback fade settings")
        )
        self.fadeActionDefaultsHelpText.setText(
            translate(
                "CueSettings",
                "Used for fade-in and fade-out actions, for cues where fade "
                "duration is set to 0.",
            )
        )

    def getSettings(self):
        return {
            "cue": {
                "interruptFade": self.interruptFadeEdit.duration(),
                "interruptFadeType": self.interruptFadeEdit.fadeType(),
                "fadeAction": self.fadeActionEdit.duration(),
                "fadeActionType": self.fadeActionEdit.fadeType(),
            }
        }

    def loadSettings(self, settings):
        self.interruptFadeEdit.setDuration(settings["cue"]["interruptFade"])
        self.interruptFadeEdit.setFadeType(settings["cue"]["interruptFadeType"])

        self.fadeActionEdit.setDuration(settings["cue"]["fadeAction"])
        self.fadeActionEdit.setFadeType(settings["cue"]["fadeActionType"])
