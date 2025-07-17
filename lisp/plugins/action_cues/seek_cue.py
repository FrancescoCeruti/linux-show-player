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
from PyQt5.QtCore import QT_TRANSLATE_NOOP, QTime
from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDateTimeEdit,
    QTimeEdit,
    QVBoxLayout,
)

from lisp.application import Application
from lisp.core.properties import Property
from lisp.cues.cue import Cue, CueAction
from lisp.cues.media_cue import MediaCue
from lisp.ui.cuelistdialog import CueSelectDialog
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class SeekCue(Cue):
    Name = QT_TRANSLATE_NOOP("CueName", "Seek Cue")
    Category = QT_TRANSLATE_NOOP("CueCategory", "Action cues")

    CueActions = (
        CueAction.Default,
        CueAction.Start,
        CueAction.Stop,
        CueAction.Pause,
        CueAction.Resume,
        CueAction.Interrupt,
    )

    target_id = Property()
    time = Property(default=-1)
    icon = Property("action-forward")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = translate("CueName", self.Name)

    def __start__(self, fade=False):
        cue = self.app.cue_model.get(self.target_id)
        if isinstance(cue, MediaCue) and self.time >= 0:
            cue.media.seek(self.time)

        return False


class SeekCueSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Seek Settings")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        self.targetCueId = -1

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
        self.seekEdit.setDisplayFormat("HH:mm:ss.zzz")
        self.seekEdit.setCurrentSection(QDateTimeEdit.SecondSection)
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
                self.targetCueId = cue.id
                self.seekEdit.setMaximumTime(
                    QTime.fromMSecsSinceStartOfDay(cue.media.duration)
                )
                self.cueLabel.setText(cue.name)

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.cueGroup, enabled)
        self.setGroupEnabled(self.seekGroup, enabled)

    def getSettings(self):
        settings = {}

        if self.isGroupEnabled(self.cueGroup):
            settings["target_id"] = self.targetCueId
        if self.isGroupEnabled(self.seekGroup):
            settings["time"] = self.seekEdit.time().msecsSinceStartOfDay()

        return settings

    def loadSettings(self, settings):
        if settings is not None:
            cue = Application().cue_model.get(settings.get("target_id"))
            if cue is not None:
                self.targetCueId = settings["target_id"]
                self.seekEdit.setMaximumTime(
                    QTime.fromMSecsSinceStartOfDay(cue.media.duration)
                )
                self.cueLabel.setText(cue.name)

            self.seekEdit.setTime(
                QTime.fromMSecsSinceStartOfDay(settings.get("time", 0))
            )


CueSettingsRegistry().add(SeekCueSettings, SeekCue)
