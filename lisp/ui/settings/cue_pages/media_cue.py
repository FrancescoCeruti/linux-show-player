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

from PyQt6.QtCore import QT_TRANSLATE_NOOP, Qt, QTime
from PyQt6.QtWidgets import (
    QDateTimeEdit,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
)

from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class MediaCueSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Media Cue")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout(self))

        # Start time
        self.startGroup = QGroupBox(self)
        self.startGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.startGroup)

        self.startEdit = QTimeEdit(self.startGroup)
        self.startEdit.setDisplayFormat("HH:mm:ss.zzz")
        self.startEdit.setCurrentSection(QDateTimeEdit.Section.SecondSection)
        self.startGroup.layout().addWidget(self.startEdit)

        self.startLabel = QLabel(self.startGroup)
        self.startLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.startGroup.layout().addWidget(self.startLabel)

        # Stop time
        self.stopGroup = QGroupBox(self)
        self.stopGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.stopGroup)

        self.stopEdit = QTimeEdit(self.stopGroup)
        self.stopEdit.setDisplayFormat("HH:mm:ss.zzz")
        self.stopEdit.setCurrentSection(QDateTimeEdit.Section.SecondSection)
        self.stopGroup.layout().addWidget(self.stopEdit)

        self.stopLabel = QLabel(self.stopGroup)
        self.stopLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stopGroup.layout().addWidget(self.stopLabel)

        # Loop
        self.loopGroup = QGroupBox(self)
        self.loopGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.loopGroup)

        self.spinLoop = QSpinBox(self.loopGroup)
        self.spinLoop.setRange(-1, 1_000_000)
        self.loopGroup.layout().addWidget(self.spinLoop)

        self.loopLabel = QLabel(self.loopGroup)
        self.loopLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loopGroup.layout().addWidget(self.loopLabel)

        self.retranslateUi()

    def retranslateUi(self):
        self.startGroup.setTitle(translate("MediaCueSettings", "Start time"))
        self.stopLabel.setText(
            translate("MediaCueSettings", "Stop position of the media")
        )
        self.stopGroup.setTitle(translate("MediaCueSettings", "Stop time"))
        self.startLabel.setText(
            translate("MediaCueSettings", "Start position of the media")
        )
        self.loopGroup.setTitle(translate("MediaCueSettings", "Loop"))
        self.loopLabel.setText(
            translate(
                "MediaCueSettings",
                "Repetition after first play (-1 = infinite)",
            )
        )

    def getSettings(self):
        settings = {}

        if self.isGroupEnabled(self.startGroup):
            time = self.startEdit.time().msecsSinceStartOfDay()
            settings["start_time"] = time
        if self.isGroupEnabled(self.stopGroup):
            time = self.stopEdit.time().msecsSinceStartOfDay()
            settings["stop_time"] = time
        if self.isGroupEnabled(self.loopGroup):
            settings["loop"] = self.spinLoop.value()

        return {"media": settings}

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.startGroup, enabled)
        self.setGroupEnabled(self.stopGroup, enabled)
        self.setGroupEnabled(self.loopGroup, enabled)

    def loadSettings(self, settings):
        settings = settings.get("media", {})

        if "loop" in settings:
            self.spinLoop.setValue(settings["loop"])
        if "start_time" in settings:
            time = self._to_qtime(settings["start_time"])
            self.startEdit.setTime(time)
        if "stop_time" in settings:
            time = self._to_qtime(settings["stop_time"])
            self.stopEdit.setTime(time)

        time = self._to_qtime(settings.get("duration", 0))
        self.startEdit.setMaximumTime(time)
        self.stopEdit.setMaximumTime(time)

    def _to_qtime(self, m_seconds):
        return QTime.fromMSecsSinceStartOfDay(m_seconds)
