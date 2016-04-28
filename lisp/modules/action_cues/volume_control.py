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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QGroupBox, \
    QPushButton, QDoubleSpinBox, QGridLayout, QComboBox, QStyledItemDelegate

from lisp.application import Application
from lisp.backends.base.media import MediaState
from lisp.core.decorators import async, synchronized_method
from lisp.core.has_properties import Property
from lisp.cues.cue import Cue, CueState, CueAction
from lisp.cues.media_cue import MediaCue
from lisp.ui.cuelistdialog import CueListDialog
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.settings_page import SettingsPage
from lisp.utils.fade_functor import ntime, FadeIn, FadeOut


class VolumeControl(Cue):
    Name = 'Volume Control'

    target_id = Property()
    fade_type = Property(default='Linear')
    volume = Property(default=.0)

    CueActions = (CueAction.Start, CueAction.Stop, CueAction.Pause,
                  CueAction.Default)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = self.Name

        self.__state = CueState.Stop
        self.__time = 0
        self.__stop = False
        self.__pause = False

    @async
    def __start__(self):
        cue = Application().cue_model.get(self.target_id)
        if isinstance(cue, MediaCue):
            volume = cue.media.element('Volume')
            if volume is not None:
                if self.duration > 0:
                    if volume.current_volume > self.volume:
                        self._fade(FadeOut[self.fade_type], volume, cue.media)
                    elif volume.current_volume < self.volume:
                        self._fade(FadeIn[self.fade_type], volume, cue.media)
                else:
                    self.__state = CueState.Running
                    self.started.emit(self)
                    volume.current_volume = self.volume
                    self.__state = CueState.Stop
                    self.end.emit(self)

    def __stop__(self):
        if self.__state == CueState.Running:
            self.__stop = True

    def __pause__(self):
        if self.__state == CueState.Running:
            self.__pause = True

    @synchronized_method(blocking=False)
    def _fade(self, functor, volume, media):
        try:
            self.started.emit(self)
            self.__state = CueState.Running

            begin = self.__time
            duration = (self.duration // 10)
            base_volume = volume.current_volume
            volume_diff = self.volume - base_volume

            while (not (self.__stop or self.__pause ) and
                   self.__time <= duration and
                   media.state == MediaState.Playing):
                time = ntime(self.__time, begin, duration)
                volume.current_volume = functor(time, volume_diff, base_volume)

                self.__time += 1
                sleep(0.01)

            if self.__stop:
                self.stopped.emit(self)
            elif self.__pause:
                self.paused.emit(self)
            else:
                self.end.emit(self)
        except Exception as e:
            self.__state = CueState.Error
            self.error.emit(self, 'Error during cue execution', str(e))
        finally:
            if not self.__pause:
                self.__state = CueState.Stop
                self.__time = 0
            else:
                self.__state = CueState.Pause

            self.__stop = False
            self.__pause = False

    def current_time(self):
        return self.__time * 10

    @Cue.state.getter
    def state(self):
        return self.__state


class VolumeSettings(SettingsPage):
    Name = 'Volume Settings'

    FadeIcons = {
        'Linear': QIcon.fromTheme('fadein_linear'),
        'Quadratic': QIcon.fromTheme('fadein_quadratic'),
        'Quadratic2': QIcon.fromTheme('fadein_quadratic2')
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.cue_id = -1

        cues = Application().cue_model.filter(MediaCue)
        self.cueDialog = CueListDialog(cues=cues, parent=self)

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
        self.volumeEdit.setMaximum(10)
        self.volumeGroup.layout().addWidget(self.volumeEdit)

        self.volumeLabel = QLabel(self.volumeGroup)
        self.volumeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.volumeGroup.layout().addWidget(self.volumeLabel)

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

        self.fadeCurveCombo = QComboBox(self.fadeGroup)
        self.fadeCurveCombo.setItemDelegate(QStyledItemDelegate())
        for key in sorted(VolumeSettings.FadeIcons.keys()):
            self.fadeCurveCombo.addItem(VolumeSettings.FadeIcons[key], key)
        self.fadeGroup.layout().addWidget(self.fadeCurveCombo, 1, 0)

        self.fadeCurveLabel = QLabel(self.fadeGroup)
        self.fadeCurveLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.fadeGroup.layout().addWidget(self.fadeCurveLabel, 1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.cueGroup.setTitle('Cue')
        self.cueButton.setText('Click to select')
        self.cueLabel.setText('Not selected')
        self.volumeGroup.setTitle('Volume')
        self.volumeLabel.setText('Volume to reach')
        self.fadeGroup.setTitle('Fade')
        self.fadeLabel.setText('Time (sec)')
        self.fadeCurveLabel.setText('Curve')

    def select_cue(self):
        if self.cueDialog.exec_() == self.cueDialog.Accepted:
            cue = self.cueDialog.selected_cues()[0]

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
            conf['volume'] = self.volumeEdit.value()
        if not (checkable and not self.fadeGroup.isCheckable()):
            conf['duration'] = self.fadeSpin.value() * 1000
            conf['fade_type'] = self.fadeCurveCombo.currentText()

        return conf

    def load_settings(self, settings):
        if settings is not None:
            cue = Application().cue_model.get(settings['target_id'])
            if cue is not None:
                self.cue_id = settings['target_id']
                self.cueLabel.setText(cue.name)

            self.volumeEdit.setValue(settings['volume'])
            self.fadeSpin.setValue(settings['duration'] / 1000)
            self.fadeCurveCombo.setCurrentText(settings['fade_type'])


CueSettingsRegistry().add_item(VolumeSettings, VolumeControl)
