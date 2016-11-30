# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from time import sleep

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QGroupBox, \
    QPushButton, QDoubleSpinBox, QGridLayout

from lisp.application import Application
from lisp.backend.audio_utils import MIN_VOLUME_DB, MAX_VOLUME_DB, linear_to_db, \
    db_to_linear
from lisp.backend.media import MediaState
from lisp.core.decorators import async, locked_method
from lisp.core.fade_functions import ntime, FadeInType, FadeOutType
from lisp.core.has_properties import Property
from lisp.cues.cue import Cue, CueAction, CueState
from lisp.cues.media_cue import MediaCue
from lisp.ui.cuelistdialog import CueSelectDialog
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.settings_page import SettingsPage
from lisp.ui.ui_utils import translate
from lisp.ui.widgets import FadeComboBox


class VolumeControl(Cue):
    Name = QT_TRANSLATE_NOOP('CueName', 'Volume Control')

    target_id = Property()
    fade_type = Property(default=FadeInType.Linear.name)
    volume = Property(default=.0)

    CueActions = (CueAction.Default, CueAction.Start, CueAction.Stop,
                  CueAction.Pause)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = translate('CueName', self.Name)

        self.__time = 0
        self.__stop = False
        self.__pause = False

    def __start__(self, fade=False):
        cue = Application().cue_model.get(self.target_id)

        if isinstance(cue, MediaCue) and cue.state & CueState.Running:
            volume = cue.media.element('Volume')
            if volume is not None:
                if self.duration > 0:
                    if volume.current_volume > self.volume:
                        self._fade(FadeOutType[self.fade_type].value,
                                   volume,
                                   cue.media)
                        return True
                    elif volume.current_volume < self.volume:
                        self._fade(FadeInType[self.fade_type].value,
                                   volume,
                                   cue.media)
                        return True
                else:
                    volume.current_volume = self.volume

        return False

    def __stop__(self, fade=False):
        self.__stop = True
        return True

    def __pause__(self, fade=False):
        self.__pause = True
        return True

    @async
    @locked_method
    def _fade(self, functor, volume, media):
        self.__stop = False
        self.__pause = False

        try:
            begin = self.__time
            duration = (self.duration // 10)
            base_volume = volume.current_volume
            volume_diff = self.volume - base_volume

            while (not (self.__stop or self.__pause) and
                           self.__time <= duration and
                           media.state == MediaState.Playing):
                time = ntime(self.__time, begin, duration)
                volume.current_volume = functor(time, volume_diff, base_volume)

                self.__time += 1
                sleep(0.01)

            if not self.__pause:
                # to avoid approximation problems
                volume.current_volume = self.volume
                if not self.__stop:
                    self._ended()
        except Exception as e:
            self._error(
                translate('VolumeControl', 'Error during cue execution'),
                str(e)
            )
        finally:
            if not self.__pause:
                self.__time = 0

    def current_time(self):
        return self.__time * 10


class VolumeSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'Volume Settings')

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

        self.cueButton = QPushButton(self.cueGroup)
        self.cueButton.clicked.connect(self.select_cue)
        self.cueGroup.layout().addWidget(self.cueButton)

        self.cueLabel = QLabel(self.cueGroup)
        self.cueLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.cueGroup.layout().addWidget(self.cueLabel)

        self.volumeGroup = QGroupBox(self)
        self.volumeGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.volumeGroup)

        self.volumeEdit = QDoubleSpinBox(self.volumeGroup)
        self.volumeEdit.setDecimals(6)
        self.volumeEdit.setMaximum(100)
        self.volumeGroup.layout().addWidget(self.volumeEdit)

        self.percentLabel = QLabel('%', self.volumeGroup)
        self.volumeGroup.layout().addWidget(self.percentLabel)

        self.volumeDbEdit = QDoubleSpinBox(self.volumeGroup)
        self.volumeDbEdit.setRange(MIN_VOLUME_DB, MAX_VOLUME_DB)
        self.volumeDbEdit.setValue(MIN_VOLUME_DB)
        self.volumeGroup.layout().addWidget(self.volumeDbEdit)

        self.dbLabel = QLabel('dB', self.volumeGroup)
        self.volumeGroup.layout().addWidget(self.dbLabel)

        self.volumeEdit.valueChanged.connect(self.__volume_change)
        self.volumeDbEdit.valueChanged.connect(self.__db_volume_change)

        # Fade
        self.fadeGroup = QGroupBox(self)
        self.fadeGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.fadeGroup)

        self.fadeSpin = QDoubleSpinBox(self.fadeGroup)
        self.fadeSpin.setMaximum(3600)
        self.fadeGroup.layout().addWidget(self.fadeSpin, 0, 0)

        self.fadeLabel = QLabel(self.fadeGroup)
        self.fadeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.fadeGroup.layout().addWidget(self.fadeLabel, 0, 1)

        self.fadeCurveCombo = FadeComboBox(parent=self.fadeGroup)
        self.fadeGroup.layout().addWidget(self.fadeCurveCombo, 1, 0)

        self.fadeCurveLabel = QLabel(self.fadeGroup)
        self.fadeCurveLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.fadeGroup.layout().addWidget(self.fadeCurveLabel, 1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.cueGroup.setTitle(translate('VolumeControl', 'Cue'))
        self.cueButton.setText(translate('VolumeControl', 'Click to select'))
        self.cueLabel.setText(translate('VolumeControl', 'Not selected'))
        self.volumeGroup.setTitle(translate('VolumeControl', 'Volume to reach'))
        self.fadeGroup.setTitle(translate('VolumeControl', 'Fade'))
        self.fadeLabel.setText(translate('VolumeControl', 'Time (sec)'))
        self.fadeCurveLabel.setText(translate('VolumeControl', 'Curve'))

    def select_cue(self):
        if self.cueDialog.exec_() == self.cueDialog.Accepted:
            cue = self.cueDialog.selected_cue()

            if cue is not None:
                self.cue_id = cue.id
                self.cueLabel.setText(cue.name)

    def enable_check(self, enabled):
        self.cueGroup.setCheckable(enabled)
        self.cueGroup.setChecked(False)

        self.volumeGroup.setCheckable(enabled)
        self.volumeGroup.setChecked(False)

        self.fadeGroup.setCheckable(enabled)
        self.volumeGroup.setChecked(False)

    def get_settings(self):
        conf = {}
        checkable = self.cueGroup.isCheckable()

        if not (checkable and not self.cueGroup.isChecked()):
            conf['target_id'] = self.cue_id
        if not (checkable and not self.volumeGroup.isCheckable()):
            conf['volume'] = self.volumeEdit.value() / 100
        if not (checkable and not self.fadeGroup.isCheckable()):
            conf['duration'] = self.fadeSpin.value() * 1000
            conf['fade_type'] = self.fadeCurveCombo.currentType()

        return conf

    def load_settings(self, settings):
        cue = Application().cue_model.get(settings.get('target_id', ''))
        if cue is not None:
            self.cue_id = settings['target_id']
            self.cueLabel.setText(cue.name)

        self.volumeEdit.setValue(settings.get('volume', 0) * 100)
        self.fadeSpin.setValue(settings.get('duration', 0) / 1000)
        self.fadeCurveCombo.setCurrentType(settings.get('fade_type', ''))

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
                self.volumeEdit.setValue(db_to_linear(value) * 100)
            finally:
                self.__v_edit_flag = False


CueSettingsRegistry().add_item(VolumeSettings, VolumeControl)
