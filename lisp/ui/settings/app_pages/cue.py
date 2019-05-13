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
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox

from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate
from lisp.ui.widgets import FadeEdit


class CueAppSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Cue Settings")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        # Interrupt
        self.interruptGroup = QGroupBox(self)
        self.interruptGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.interruptGroup)

        self.interruptFadeEdit = FadeEdit(self.interruptGroup)
        self.interruptGroup.layout().addWidget(self.interruptFadeEdit)

        # Action
        self.actionGroup = QGroupBox(self)
        self.actionGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.actionGroup)

        self.fadeActionEdit = FadeEdit(self.actionGroup)
        self.actionGroup.layout().addWidget(self.fadeActionEdit)

        self.retranslateUi()

    def retranslateUi(self):
        self.interruptGroup.setTitle(translate("CueSettings", "Interrupt fade"))
        self.actionGroup.setTitle(translate("CueSettings", "Fade actions"))

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
