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

from PyQt5 import QtCore
from PyQt5.QtCore import QTime, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QGroupBox,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QTimeEdit,
)

from lisp.application import Application
from lisp.core.properties import Property
from lisp.cues.cue import Cue
from lisp.cues.media_cue import MediaCue
from lisp.ui.cuelistdialog import CueSelectDialog
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class SeekCue(Cue):
    Name = QT_TRANSLATE_NOOP("CueName", "Seek Cue")
    Category = QT_TRANSLATE_NOOP("CueCategory", "Action cues")

    target_id = Property()
    time = Property(default=-1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = translate("CueName", self.Name)

    def __start__(self, fade=False):
        cue = Application().cue_model.get(self.target_id)
        if isinstance(cue, MediaCue) and self.time >= 0:
            cue.media.seek(self.time)

        return False


class SeekCueSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Seek Settings")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        self.cue_id = -1

        self.cueDialog = CueSelectDialog(
            cues=Application().cue_model.filter(MediaCue), parent=self
        )

        self.cueGroup = QGroupBox(self)
        self.cueGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.cueGroup)

        self.cueButton = QPushButton(self.cueGroup)
        self.cueButton.clicked.connect(self.select_cue)
        self.cueGroup.layout().addWidget(self.cueButton)

        self.cueLabel = QLabel(self.cueGroup)
        self.cueLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.cueGroup.layout().addWidget(self.cueLabel)

        self.seekGroup = QGroupBox(self)
        self.seekGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.seekGroup)

        self.seekEdit = QTimeEdit(self.seekGroup)
        self.seekEdit.setDisplayFormat("HH.mm.ss.zzz")
        self.seekGroup.layout().addWidget(self.seekEdit)

        self.seekLabel = QLabel(self.seekGroup)
        self.seekLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.seekGroup.layout().addWidget(self.seekLabel)

        self.retranslateUi()

    def retranslateUi(self):
        self.cueGroup.setTitle(translate("SeekCue", "Cue"))
        self.cueButton.setText(translate("SeekCue", "Click to select"))
        self.cueLabel.setText(translate("SeekCue", "Not selected"))
        self.seekGroup.setTitle(translate("SeekCue", "Seek"))
        self.seekLabel.setText(translate("SeekCue", "Time to reach"))

    def select_cue(self):
        if self.cueDialog.exec() == self.cueDialog.Accepted:
            cue = self.cueDialog.selected_cue()

            if cue is not None:
                self.cue_id = cue.id
                self.seekEdit.setMaximumTime(
                    QTime.fromMSecsSinceStartOfDay(cue.media.duration)
                )
                self.cueLabel.setText(cue.name)

    def enableCheck(self, enabled):
        self.cueGroup.setCheckable(enabled)
        self.cueGroup.setChecked(False)

        self.seekGroup.setCheckable(enabled)
        self.seekGroup.setChecked(False)

    def getSettings(self):
        return {
            "target_id": self.cue_id,
            "time": self.seekEdit.time().msecsSinceStartOfDay(),
        }

    def loadSettings(self, settings):
        if settings is not None:
            cue = Application().cue_model.get(settings.get("target_id"))
            if cue is not None:
                self.cue_id = settings["target_id"]
                self.seekEdit.setMaximumTime(
                    QTime.fromMSecsSinceStartOfDay(cue.media.duration)
                )
                self.cueLabel.setText(cue.name)

            self.seekEdit.setTime(
                QTime.fromMSecsSinceStartOfDay(settings.get("time", 0))
            )


CueSettingsRegistry().add(SeekCueSettings, SeekCue)
