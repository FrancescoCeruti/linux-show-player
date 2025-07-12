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

import logging

from PyQt5.QtCore import QT_TRANSLATE_NOOP, Qt
from PyQt5.QtWidgets import (
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from lisp.application import Application
from lisp.backend.audio_utils import (
    MAX_VOLUME,
    MAX_VOLUME_DB,
    MIN_VOLUME_DB,
    db_to_linear,
    linear_to_db,
)
from lisp.core.decorators import async_function
from lisp.core.fade_functions import FadeInType, FadeOutType
from lisp.core.fader import DummyFader
from lisp.core.properties import Property
from lisp.cues.cue import Cue, CueAction
from lisp.cues.media_cue import MediaCue
from lisp.ui.cuelistdialog import CueSelectDialog
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate
from lisp.ui.widgets import FadeEdit

logger = logging.getLogger(__name__)


class VolumeControl(Cue):
    Name = QT_TRANSLATE_NOOP("CueName", "Volume Control")
    Category = QT_TRANSLATE_NOOP("CueCategory", "Action cues")

    target_id = Property()
    fade_type = Property(default=FadeInType.Linear.name)
    volume = Property(default=0.0)
    icon = Property("faders")

    CueActions = (
        CueAction.Default,
        CueAction.Start,
        CueAction.Stop,
        CueAction.Pause,
        CueAction.Resume,
        CueAction.Resume,
        CueAction.Interrupt,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = translate("CueName", self.Name)

        self.__fader = None
        self.__init_fader()

    def __init_fader(self):
        cue = self.app.cue_model.get(self.target_id)

        if isinstance(cue, MediaCue):
            volume = cue.media.element("Volume")
            if volume is not None:
                self.__fader = volume.get_fader("live_volume")
                return True

        self.__fader = DummyFader()

        return False

    def __start__(self, fade=False):
        if self.__init_fader():
            if self.duration > 0:
                if self.__fader.target.live_volume > self.volume:
                    self.__fade(FadeOutType[self.fade_type])
                    return True
                elif self.__fader.target.live_volume < self.volume:
                    self.__fade(FadeInType[self.fade_type])
                    return True
            else:
                self.__fader.target.live_volume = self.volume

        return False

    def __stop__(self, fade=False):
        self.__fader.stop()
        return True

    __interrupt__ = __stop__

    @async_function
    def __fade(self, fade_type):
        try:
            self.__fader.prepare()
            ended = self.__fader.fade(
                round(self.duration / 1000, 2), self.volume, fade_type
            )

            if ended:
                self._ended()
        except Exception:
            logger.exception(
                translate("VolumeControlError", "Error during cue execution.")
            )
            self._error()

    def current_time(self):
        return self.__fader.current_time()


class VolumeSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Volume Settings")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.__v_edit_flag = False
        self.cue_id = -1

        cues = Application().cue_model.filter(MediaCue)
        self.cueDialog = CueSelectDialog(cues=cues, parent=self)

        self.cueGroup = QGroupBox(self)
        self.cueGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.cueGroup)

        self.cueLabel = QLabel(self.cueGroup)
        self.cueLabel.setAlignment(Qt.AlignCenter)
        self.cueLabel.setStyleSheet("font-weight: bold;")
        self.cueGroup.layout().addWidget(self.cueLabel)

        self.cueButton = QPushButton(self.cueGroup)
        self.cueButton.clicked.connect(self.select_cue)
        self.cueGroup.layout().addWidget(self.cueButton)

        self.volumeGroup = QGroupBox(self)
        self.volumeGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.volumeGroup)

        self.volumePercentEdit = QDoubleSpinBox(self.volumeGroup)
        self.volumePercentEdit.setSuffix(" %")
        self.volumePercentEdit.setDecimals(6)
        self.volumePercentEdit.setMaximum(MAX_VOLUME * 100)
        self.volumeGroup.layout().addWidget(self.volumePercentEdit)

        self.volumeGroup.layout().setSpacing(100)

        self.volumeDbEdit = QDoubleSpinBox(self.volumeGroup)
        self.volumeDbEdit.setSuffix(" dB")
        self.volumeDbEdit.setRange(MIN_VOLUME_DB, MAX_VOLUME_DB)
        self.volumeDbEdit.setValue(MIN_VOLUME_DB)
        self.volumeGroup.layout().addWidget(self.volumeDbEdit)

        self.volumePercentEdit.valueChanged.connect(self.__volume_change)
        self.volumeDbEdit.valueChanged.connect(self.__db_volume_change)

        # Fade
        self.fadeGroup = QGroupBox(self)
        self.fadeGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.fadeGroup)

        self.fadeEdit = FadeEdit(self.fadeGroup)
        self.fadeGroup.layout().addWidget(self.fadeEdit)

        self.retranslateUi()

    def retranslateUi(self):
        self.cueGroup.setTitle(translate("VolumeControl", "Cue"))
        self.cueButton.setText(translate("VolumeControl", "Click to select"))
        self.cueLabel.setText(translate("VolumeControl", "Not selected"))
        self.volumeGroup.setTitle(translate("VolumeControl", "Volume to reach"))
        self.fadeGroup.setTitle(translate("VolumeControl", "Fade"))

    def select_cue(self):
        if self.cueDialog.exec() == self.cueDialog.Accepted:
            cue = self.cueDialog.selected_cue()

            if cue is not None:
                self.cue_id = cue.id
                self.cueLabel.setText(cue.name)

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.cueGroup, enabled)
        self.setGroupEnabled(self.volumeGroup, enabled)
        self.setGroupEnabled(self.fadeGroup, enabled)

    def getSettings(self):
        settings = {}

        if self.isGroupEnabled(self.cueGroup):
            settings["target_id"] = self.cue_id
        if self.isGroupEnabled(self.volumeGroup):
            settings["volume"] = self.volumePercentEdit.value() / 100
        if self.isGroupEnabled(self.fadeGroup):
            settings["duration"] = int(self.fadeEdit.duration() * 1000)
            settings["fade_type"] = self.fadeEdit.fadeType()

        return settings

    def loadSettings(self, settings):
        cue = Application().cue_model.get(settings.get("target_id", ""))
        if cue is not None:
            self.cue_id = settings["target_id"]
            self.cueLabel.setText(cue.name)

        self.volumePercentEdit.setValue(settings.get("volume", 0) * 100)
        self.fadeEdit.setDuration(settings.get("duration", 0) / 1000)
        self.fadeEdit.setFadeType(settings.get("fade_type", ""))

    def __volume_change(self, value):
        if not self.__v_edit_flag:
            try:
                self.__v_edit_flag = True
                self.volumeDbEdit.setValue(linear_to_db(value / 100))
            finally:
                self.__v_edit_flag = False

    def __db_volume_change(self, value):
        if not self.__v_edit_flag:
            try:
                self.__v_edit_flag = True
                self.volumePercentEdit.setValue(db_to_linear(value) * 100)
            finally:
                self.__v_edit_flag = False


CueSettingsRegistry().add(VolumeSettings, VolumeControl)
