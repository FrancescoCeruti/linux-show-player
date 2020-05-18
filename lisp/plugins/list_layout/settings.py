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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QCheckBox,
    QLabel,
    QKeySequenceEdit,
    QGridLayout,
    QSpinBox,
    QWidget,
    QScrollArea,
)

from lisp.cues.cue import CueAction
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate
from lisp.ui.widgets import CueActionComboBox


class ListLayoutSettings(QScrollArea, SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "List Layout")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWidgetResizable(True)
        self.contentWidget = QWidget(self)
        self.contentWidget.setLayout(QVBoxLayout())
        self.contentWidget.layout().setAlignment(Qt.AlignTop)

        self.defaultBehaviorsGroup = QGroupBox(self.contentWidget)
        self.defaultBehaviorsGroup.setLayout(QVBoxLayout())
        self.contentWidget.layout().addWidget(self.defaultBehaviorsGroup)

        self.showDbMeters = QCheckBox(self.defaultBehaviorsGroup)
        self.defaultBehaviorsGroup.layout().addWidget(self.showDbMeters)

        self.showAccurate = QCheckBox(self.defaultBehaviorsGroup)
        self.defaultBehaviorsGroup.layout().addWidget(self.showAccurate)

        self.showSeek = QCheckBox(self.defaultBehaviorsGroup)
        self.defaultBehaviorsGroup.layout().addWidget(self.showSeek)

        self.autoNext = QCheckBox(self.defaultBehaviorsGroup)
        self.defaultBehaviorsGroup.layout().addWidget(self.autoNext)

        self.selectionMode = QCheckBox(self.defaultBehaviorsGroup)
        self.defaultBehaviorsGroup.layout().addWidget(self.selectionMode)

        self.behaviorsGroup = QGroupBox(self.contentWidget)
        self.behaviorsGroup.setLayout(QGridLayout())
        self.behaviorsGroup.layout().setColumnStretch(0, 1)
        self.behaviorsGroup.layout().setColumnStretch(1, 1)
        self.contentWidget.layout().addWidget(self.behaviorsGroup)

        self.useWaveformSeek = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.useWaveformSeek, 0, 0, 1, 2)

        self.goKeyDisabledWhilePlaying = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(
            self.goKeyDisabledWhilePlaying, 1, 0, 1, 2
        )

        self.goKeyLabel = QLabel(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.goKeyLabel, 2, 0)
        self.goKeyEdit = QKeySequenceEdit(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.goKeyEdit, 2, 1)

        self.goActionLabel = QLabel(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.goActionLabel, 3, 0)
        self.goActionCombo = CueActionComboBox(
            actions=(CueAction.Default, CueAction.Start, CueAction.FadeInStart),
            mode=CueActionComboBox.Mode.Value,
        )
        self.behaviorsGroup.layout().addWidget(self.goActionCombo, 3, 1)

        self.goDelayLabel = QLabel(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.goDelayLabel, 4, 0)
        self.goDelaySpin = QSpinBox(self.behaviorsGroup)
        self.goDelaySpin.setMaximum(10000)
        self.behaviorsGroup.layout().addWidget(self.goDelaySpin, 4, 1)

        self.useFadeGroup = QGroupBox(self.contentWidget)
        self.useFadeGroup.setLayout(QGridLayout())
        self.contentWidget.layout().addWidget(self.useFadeGroup)

        # Fade settings
        self.stopCueFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.stopCueFade, 0, 0)
        self.pauseCueFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.pauseCueFade, 1, 0)
        self.resumeCueFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.resumeCueFade, 2, 0)
        self.interruptCueFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.interruptCueFade, 3, 0)

        self.setWidget(self.contentWidget)
        self.retranslateUi()

    def retranslateUi(self):
        self.defaultBehaviorsGroup.setTitle(
            translate(
                "ListLayout", "Default behaviors (applied to new sessions)"
            )
        )
        self.showDbMeters.setText(translate("ListLayout", "Show dB-meters"))
        self.showAccurate.setText(translate("ListLayout", "Show accurate time"))
        self.showSeek.setText(translate("ListLayout", "Show seek-bars"))
        self.autoNext.setText(translate("ListLayout", "Auto-select next cue"))
        self.selectionMode.setText(
            translate("ListLayout", "Enable selection mode")
        )

        self.behaviorsGroup.setTitle(translate("ListLayout", "Behaviors"))
        self.useWaveformSeek.setText(
            translate("ListLayout", "Use waveform seek-bars")
        )
        self.goKeyDisabledWhilePlaying.setText(
            translate("ListLayout", "GO Key Disabled While Playing")
        )
        self.goKeyLabel.setText(translate("ListLayout", "GO Key:"))
        self.goActionLabel.setText(translate("ListLayout", "GO Action:"))
        self.goDelayLabel.setText(
            translate("ListLayout", "GO minimum interval (ms):")
        )

        self.useFadeGroup.setTitle(
            translate("ListLayout", "Use fade (buttons)")
        )
        self.stopCueFade.setText(translate("ListLayout", "Stop Cue"))
        self.pauseCueFade.setText(translate("ListLayout", "Pause Cue"))
        self.resumeCueFade.setText(translate("ListLayout", "Resume Cue"))
        self.interruptCueFade.setText(translate("ListLayout", "Interrupt Cue"))

    def loadSettings(self, settings):
        self.showDbMeters.setChecked(settings["show"]["dBMeters"])
        self.showAccurate.setChecked(settings["show"]["accurateTime"])
        self.showSeek.setChecked(settings["show"]["seekSliders"])
        self.useWaveformSeek.setChecked(settings["show"]["waveformSlider"])
        self.autoNext.setChecked(settings["autoContinue"])
        self.selectionMode.setChecked(settings["selectionMode"])

        self.goKeyDisabledWhilePlaying.setChecked(
            settings["goKeyDisabledWhilePlaying"]
        )
        self.goKeyEdit.setKeySequence(
            QKeySequence(settings["goKey"], QKeySequence.NativeText)
        )
        self.goActionCombo.setCurrentItem(settings["goAction"])
        self.goDelaySpin.setValue(settings["goDelay"])

        self.stopCueFade.setChecked(settings["stopCueFade"])
        self.pauseCueFade.setChecked(settings["pauseCueFade"])
        self.resumeCueFade.setChecked(settings["resumeCueFade"])
        self.interruptCueFade.setChecked(settings["interruptCueFade"])

    def getSettings(self):
        return {
            "show": {
                "accurateTime": self.showAccurate.isChecked(),
                "dBMeters": self.showDbMeters.isChecked(),
                "seekSliders": self.showSeek.isChecked(),
                "waveformSlider": self.useWaveformSeek.isChecked(),
            },
            "autoContinue": self.autoNext.isChecked(),
            "selectionMode": self.selectionMode.isChecked(),
            "goKey": self.goKeyEdit.keySequence().toString(
                QKeySequence.NativeText
            ),
            "goAction": self.goActionCombo.currentItem(),
            "goDelay": self.goDelaySpin.value(),
            "goKeyDisabledWhilePlaying": self.goKeyDisabledWhilePlaying.isChecked(),
            "stopCueFade": self.stopCueFade.isChecked(),
            "pauseCueFade": self.pauseCueFade.isChecked(),
            "resumeCueFade": self.resumeCueFade.isChecked(),
            "interruptCueFade": self.interruptCueFade.isChecked(),
        }
