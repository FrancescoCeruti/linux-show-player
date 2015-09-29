# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QGroupBox, \
    QPushButton, QDoubleSpinBox, QGridLayout, QComboBox, QStyledItemDelegate

from lisp.application import Application
from lisp.backends.base.media import MediaState
from lisp.core.decorators import async, synchronized_method
from lisp.core.has_properties import Property
from lisp.cues.cue import Cue
from lisp.cues.media_cue import MediaCue
from lisp.layouts.cue_layout import CueLayout
from lisp.ui.cuelistdialog import CueListDialog
from lisp.ui.settings.section import SettingsSection
from lisp.utils.fade_functor import ntime, fade_linear, fadein_quad, \
    fade_inout_quad, fadeout_quad


class VolumeControl(Cue):
    Name = 'Volume Control'

    FadeIn = {'Linear': fade_linear, 'Quadratic': fadein_quad,
              'Quadratic2': fade_inout_quad}
    FadeOut = {'Linear': fade_linear, 'Quadratic': fadeout_quad,
               'Quadratic2': fade_inout_quad}

    target_id = Property()
    fade_type = Property(default='Linear')
    fade = Property(default=.0)
    volume = Property(default=.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = self.Name

    def execute(self, action=Cue.CueAction.Default):
        self.on_execute.emit(self, action)

        cue = Application().layout.get_cue_by_id(self.target_id)
        if isinstance(cue, MediaCue):
            volume = cue.media.element('Volume')
            if volume is not None:
                if self.fade > 0:
                    if volume.current_volume > self.volume:
                        self._fadeout(volume, cue.media)
                    elif volume.current_volume < self.volume:
                        self._fadein(volume, cue.media)
                else:
                    volume.current_volume = self.volume

        self.executed.emit(self, action)

    @async
    @synchronized_method(lock_name='__fade_lock', blocking=False)
    def _fadein(self, volume, media):
        functor = VolumeControl.FadeIn[self.fade_type]
        duration = self.fade * 100
        base_volume = volume.current_volume
        volume_diff = self.volume - base_volume
        time = 0

        while time <= duration and media.state == MediaState.Playing:
            volume.current_volume = functor(ntime(time, 0, duration),
                                            volume_diff, base_volume)
            time += 1
            sleep(0.01)

    @async
    @synchronized_method(lock_name='__fade_lock', blocking=False)
    def _fadeout(self, volume, media):
        functor = VolumeControl.FadeOut[self.fade_type]
        duration = self.fade * 100
        base_volume = volume.current_volume
        volume_diff = self.volume - base_volume
        time = 0

        while time <= duration and media.state == MediaState.Playing:
            volume.current_volume = functor(ntime(time, 0, duration),
                                            volume_diff, base_volume)
            time += 1
            sleep(0.01)


class VolumeSettings(SettingsSection):
    Name = 'Volume Settings'

    FadeIcons = {'Linear': QIcon.fromTheme('fadein_linear'),
                'Quadratic': QIcon.fromTheme('fadein_quadratic'),
                'Quadratic2': QIcon.fromTheme('fadein_quadratic2')}

    def __init__(self, size, cue=None, parent=None):
        super().__init__(size, cue=cue, parent=parent)

        self.cue_id = -1
        self.setLayout(QVBoxLayout(self))

        self.app_layout = Application().layout
        self.cueDialog = CueListDialog(parent=self)
        self.cueDialog.add_cues(self.app_layout.get_cues(cue_class=MediaCue))

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

    def enable_check(self, enable):
        self.cueGroup.setCheckable(enable)
        self.cueGroup.setChecked(False)

        self.volumeGroup.setCheckable(enable)
        self.volumeGroup.setChecked(False)

    def get_configuration(self):
        return {'target_id': self.cue_id,
                'volume': self.volumeEdit.value(),
                'fade': self.fadeSpin.value(),
                'fade_type': self.fadeCurveCombo.currentText()}

    def set_configuration(self, conf):
        if conf is not None:
            cue = self.app_layout.get_cue_by_id(conf['target_id'])
            if cue is not None:
                self.cue_id = conf['target_id']
                self.cueLabel.setText(cue.name)

            self.volumeEdit.setValue(conf['volume'])
            self.fadeSpin.setValue(conf['fade'])
            self.fadeCurveCombo.setCurrentText(conf['fade_type'])


CueLayout.add_settings_section(VolumeSettings, VolumeControl)
