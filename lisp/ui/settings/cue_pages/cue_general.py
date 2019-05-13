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
from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QDoubleSpinBox,
)

from lisp.cues.cue import CueAction
from lisp.ui.settings.pages import (
    CueSettingsPage,
    SettingsPagesTabWidget,
    CuePageMixin,
)
from lisp.ui.ui_utils import translate
from lisp.ui.widgets import (
    FadeComboBox,
    CueActionComboBox,
    CueNextActionComboBox,
    FadeEdit,
)


class CueGeneralSettingsPage(SettingsPagesTabWidget, CuePageMixin):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Cue")

    def __init__(self, cueType, **kwargs):
        super().__init__(cueType=cueType, **kwargs)
        self.addPage(CueBehavioursPage(self.cueType))
        self.addPage(CueWaitsPage(self.cueType))
        self.addPage(CueFadePage(self.cueType))


class CueBehavioursPage(CueSettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Behaviours")

    def __init__(self, cueType, **kwargs):
        super().__init__(cueType, **kwargs)
        self.setLayout(QVBoxLayout())

        # Start-Action
        self.startActionGroup = QGroupBox(self)
        self.startActionGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.startActionGroup)

        self.startActionCombo = CueActionComboBox(
            {CueAction.Start, CueAction.FadeInStart}
            .intersection(self.cueType.CueActions)
            .union({CueAction.DoNothing}),
            mode=CueActionComboBox.Mode.Value,
            parent=self.startActionGroup,
        )
        self.startActionCombo.setEnabled(self.startActionCombo.count() > 1)
        self.startActionGroup.layout().addWidget(self.startActionCombo)

        self.startActionLabel = QLabel(self.startActionGroup)
        self.startActionLabel.setAlignment(Qt.AlignCenter)
        self.startActionGroup.layout().addWidget(self.startActionLabel)

        # Stop-Action
        self.stopActionGroup = QGroupBox(self)
        self.stopActionGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.stopActionGroup)

        self.stopActionCombo = CueActionComboBox(
            {
                CueAction.Stop,
                CueAction.Pause,
                CueAction.FadeOutStop,
                CueAction.FadeOutPause,
            }
            .intersection(self.cueType.CueActions)
            .union({CueAction.DoNothing}),
            mode=CueActionComboBox.Mode.Value,
            parent=self.stopActionGroup,
        )
        self.stopActionCombo.setEnabled(self.stopActionCombo.count() > 1)
        self.stopActionGroup.layout().addWidget(self.stopActionCombo)

        self.stopActionLabel = QLabel(self.stopActionGroup)
        self.stopActionLabel.setAlignment(Qt.AlignCenter)
        self.stopActionGroup.layout().addWidget(self.stopActionLabel)

        self.layout().addSpacing(150)
        self.setEnabled(
            self.stopActionCombo.isEnabled()
            and self.startActionCombo.isEnabled()
        )

        self.retranslateUi()

    def retranslateUi(self):
        # Start-Action
        self.startActionGroup.setTitle(translate("CueSettings", "Start action"))
        self.startActionLabel.setText(
            translate("CueSettings", "Default action to start the cue")
        )

        # Stop-Action
        self.stopActionGroup.setTitle(translate("CueSettings", "Stop action"))
        self.stopActionLabel.setText(
            translate("CueSettings", "Default action to stop the cue")
        )

    def enableCheck(self, enabled):
        self.startActionGroup.setCheckable(enabled)
        self.startActionGroup.setChecked(False)
        self.stopActionGroup.setCheckable(enabled)
        self.stopActionGroup.setChecked(False)

    def getSettings(self):
        settings = {}
        checkable = self.startActionGroup.isCheckable()

        if (
            not checkable or self.startActionGroup.isChecked()
        ) and self.startActionCombo.isEnabled():
            settings[
                "default_start_action"
            ] = self.startActionCombo.currentItem()
        if (
            not checkable or self.stopActionGroup.isChecked()
        ) and self.stopActionCombo.isEnabled():
            settings["default_stop_action"] = self.stopActionCombo.currentItem()

        return settings

    def loadSettings(self, settings):
        self.startActionCombo.setCurrentItem(
            settings.get("default_start_action", "")
        )
        self.stopActionCombo.setCurrentItem(
            settings.get("default_stop_action", "")
        )


class CueWaitsPage(CueSettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Pre/Post Wait")

    def __init__(self, cueType, **kwargs):
        super().__init__(cueType=cueType, **kwargs)
        self.setLayout(QVBoxLayout())

        # Pre wait
        self.preWaitGroup = QGroupBox(self)
        self.preWaitGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.preWaitGroup)

        self.preWaitSpin = QDoubleSpinBox(self.preWaitGroup)
        self.preWaitSpin.setMaximum(3600 * 24)
        self.preWaitGroup.layout().addWidget(self.preWaitSpin)

        self.preWaitLabel = QLabel(self.preWaitGroup)
        self.preWaitLabel.setAlignment(Qt.AlignCenter)
        self.preWaitGroup.layout().addWidget(self.preWaitLabel)

        # Post wait
        self.postWaitGroup = QGroupBox(self)
        self.postWaitGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.postWaitGroup)

        self.postWaitSpin = QDoubleSpinBox(self.postWaitGroup)
        self.postWaitSpin.setMaximum(3600 * 24)
        self.postWaitGroup.layout().addWidget(self.postWaitSpin)

        self.postWaitLabel = QLabel(self.postWaitGroup)
        self.postWaitLabel.setAlignment(Qt.AlignCenter)
        self.postWaitGroup.layout().addWidget(self.postWaitLabel)

        # Next action
        self.nextActionGroup = QGroupBox(self)
        self.nextActionGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.nextActionGroup)

        self.nextActionCombo = CueNextActionComboBox(
            parent=self.nextActionGroup
        )
        self.nextActionGroup.layout().addWidget(self.nextActionCombo)

        self.retranslateUi()

    def retranslateUi(self):
        # PreWait
        self.preWaitGroup.setTitle(translate("CueSettings", "Pre wait"))
        self.preWaitLabel.setText(
            translate("CueSettings", "Wait before cue execution")
        )
        # PostWait
        self.postWaitGroup.setTitle(translate("CueSettings", "Post wait"))
        self.postWaitLabel.setText(
            translate("CueSettings", "Wait after cue execution")
        )
        # NextAction
        self.nextActionGroup.setTitle(translate("CueSettings", "Next action"))

    def enableCheck(self, enabled):
        self.preWaitGroup.setCheckable(enabled)
        self.preWaitGroup.setChecked(False)
        self.postWaitGroup.setCheckable(enabled)
        self.postWaitGroup.setChecked(False)
        self.nextActionGroup.setCheckable(enabled)
        self.nextActionGroup.setChecked(False)

    def loadSettings(self, settings):
        self.preWaitSpin.setValue(settings.get("pre_wait", 0))
        self.postWaitSpin.setValue(settings.get("post_wait", 0))
        self.nextActionCombo.setCurrentAction(settings.get("next_action", ""))

    def getSettings(self):
        settings = {}
        checkable = self.preWaitGroup.isCheckable()

        if not checkable or self.preWaitGroup.isChecked():
            settings["pre_wait"] = self.preWaitSpin.value()
        if not checkable or self.postWaitGroup.isChecked():
            settings["post_wait"] = self.postWaitSpin.value()
        if not checkable or self.nextActionGroup.isChecked():
            settings["next_action"] = self.nextActionCombo.currentData()

        return settings


class CueFadePage(CueSettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Fade In/Out")

    def __init__(self, cueType, **kwargs):
        super().__init__(cueType, **kwargs)
        self.setLayout(QVBoxLayout())

        # FadeIn
        self.fadeInGroup = QGroupBox(self)
        self.fadeInGroup.setEnabled(CueAction.FadeInStart in cueType.CueActions)
        self.fadeInGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.fadeInGroup)

        self.fadeInEdit = FadeEdit(
            self.fadeInGroup, mode=FadeComboBox.Mode.FadeIn
        )
        self.fadeInGroup.layout().addWidget(self.fadeInEdit)

        # FadeOut
        self.fadeOutGroup = QGroupBox(self)
        self.fadeOutGroup.setEnabled(
            CueAction.FadeOutPause in cueType.CueActions
            or CueAction.FadeOutStop in cueType.CueActions
        )
        self.fadeOutGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.fadeOutGroup)

        self.fadeOutEdit = FadeEdit(
            self.fadeOutGroup, mode=FadeComboBox.Mode.FadeOut
        )
        self.fadeOutGroup.layout().addWidget(self.fadeOutEdit)

        self.retranslateUi()

    def retranslateUi(self):
        # FadeIn/Out
        self.fadeInGroup.setTitle(translate("FadeSettings", "Fade In"))
        self.fadeOutGroup.setTitle(translate("FadeSettings", "Fade Out"))

    def loadSettings(self, settings):
        self.fadeInEdit.setFadeType(settings.get("fadein_type", ""))
        self.fadeInEdit.setDuration(settings.get("fadein_duration", 0))
        self.fadeOutEdit.setFadeType(settings.get("fadeout_type", ""))
        self.fadeOutEdit.setDuration(settings.get("fadeout_duration", 0))

    def enableCheck(self, enabled):
        self.fadeInGroup.setCheckable(enabled)
        self.fadeInGroup.setChecked(False)
        self.fadeOutGroup.setCheckable(enabled)
        self.fadeOutGroup.setChecked(False)

    def getSettings(self):
        settings = {}
        checkable = self.fadeInGroup.isCheckable()

        if not checkable or self.fadeInGroup.isChecked():
            settings["fadein_type"] = self.fadeInEdit.fadeType()
            settings["fadein_duration"] = self.fadeInEdit.duration()
        if not checkable or self.fadeInGroup.isChecked():
            settings["fadeout_type"] = self.fadeOutEdit.fadeType()
            settings["fadeout_duration"] = self.fadeOutEdit.duration()

        return settings
