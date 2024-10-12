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

from PyQt6.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt6.QtWidgets import QVBoxLayout, QGroupBox, QCheckBox

from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class LayoutsSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Layouts")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        self.useFadeGroup = QGroupBox(self)
        self.useFadeGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.useFadeGroup)

        self.stopAllFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.stopAllFade)

        self.interruptAllFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.interruptAllFade)

        self.pauseAllFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.pauseAllFade)

        self.resumeAllFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.resumeAllFade)

        self.retranslateUi()

    def retranslateUi(self):
        self.useFadeGroup.setTitle(translate("ListLayout", "Layout actions"))
        self.stopAllFade.setText(
            translate("ListLayout", "Fade out when stopping all cues")
        )
        self.interruptAllFade.setText(
            translate("ListLayout", "Fade out when interrupting all cues")
        )
        self.pauseAllFade.setText(
            translate("ListLayout", "Fade out when pausing all cues")
        )
        self.resumeAllFade.setText(
            translate("ListLayout", "Fade in when resuming all cues")
        )

    def loadSettings(self, settings):
        self.stopAllFade.setChecked(settings["layout"]["stopAllFade"])
        self.pauseAllFade.setChecked(settings["layout"]["pauseAllFade"])
        self.resumeAllFade.setChecked(settings["layout"]["resumeAllFade"])
        self.interruptAllFade.setChecked(settings["layout"]["interruptAllFade"])

    def getSettings(self):
        return {
            "layout": {
                "stopAllFade": self.stopAllFade.isChecked(),
                "pauseAllFade": self.pauseAllFade.isChecked(),
                "resumeAllFade": self.resumeAllFade.isChecked(),
                "interruptAllFade": self.interruptAllFade.isChecked(),
            }
        }
