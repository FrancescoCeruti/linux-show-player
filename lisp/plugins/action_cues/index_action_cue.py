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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QLabel,
    QSpinBox,
    QGridLayout,
    QVBoxLayout,
    QLineEdit,
)

from lisp.application import Application
from lisp.core.properties import Property
from lisp.cues.cue import Cue, CueAction
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate
from lisp.ui.widgets import CueActionComboBox


class IndexActionCue(Cue):
    Name = QT_TRANSLATE_NOOP("CueName", "Index Action")
    Category = QT_TRANSLATE_NOOP("CueCategory", "Action cues")

    target_index = Property(default=0)
    relative = Property(default=True)
    action = Property(default=CueAction.Stop.value)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = translate("CueName", self.Name)

    def __start__(self, fade=False):
        if self.relative:
            index = self.index + self.target_index
        else:
            index = self.target_index

        try:
            cue = Application().layout.cue_at(index)
            if cue is not self:
                cue.execute(CueAction(self.action))
        except IndexError:
            pass


class IndexActionCueSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Action Settings")

    DEFAULT_SUGGESTION = translate("IndexActionCue", "No suggestion")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self._cue_index = 0
        self._target_class = Cue

        self.indexGroup = QGroupBox(self)
        self.indexGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.indexGroup)

        self.relativeCheck = QCheckBox(self.indexGroup)
        self.relativeCheck.stateChanged.connect(self._relative_changed)
        self.indexGroup.layout().addWidget(self.relativeCheck, 0, 0, 1, 2)

        self.targetIndexSpin = QSpinBox(self)
        self.targetIndexSpin.valueChanged.connect(self._target_changed)
        self.targetIndexSpin.setRange(0, len(Application().cue_model) - 1)
        self.indexGroup.layout().addWidget(self.targetIndexSpin, 1, 0)

        self.targetIndexLabel = QLabel(self)
        self.targetIndexLabel.setAlignment(Qt.AlignCenter)
        self.indexGroup.layout().addWidget(self.targetIndexLabel, 1, 1)

        self.actionGroup = QGroupBox(self)
        self.actionGroup.setLayout(QVBoxLayout(self.actionGroup))
        self.layout().addWidget(self.actionGroup)

        self.actionCombo = CueActionComboBox(
            self._target_class.CueActions,
            mode=CueActionComboBox.Mode.Value,
            parent=self.actionGroup,
        )
        self.actionGroup.layout().addWidget(self.actionCombo)

        self.suggestionGroup = QGroupBox(self)
        self.suggestionGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.suggestionGroup)

        self.suggestionPreview = QLineEdit(self.suggestionGroup)
        self.suggestionPreview.setAlignment(Qt.AlignCenter)
        self.suggestionPreview.setText(
            IndexActionCueSettings.DEFAULT_SUGGESTION
        )
        self.suggestionGroup.layout().addWidget(self.suggestionPreview)

        self.actionCombo.currentTextChanged.connect(self._update_suggestion)

        self.retranslateUi()

    def retranslateUi(self):
        self.indexGroup.setTitle(translate("IndexActionCue", "Index"))
        self.relativeCheck.setText(
            translate("IndexActionCue", "Use a relative index")
        )
        self.targetIndexLabel.setText(
            translate("IndexActionCue", "Target index")
        )
        self.actionGroup.setTitle(translate("IndexActionCue", "Action"))

        self.suggestionGroup.setTitle(
            translate("IndexActionCue", "Suggested cue name")
        )

    def enableCheck(self, enabled):
        self.indexGroup.setChecked(enabled)
        self.indexGroup.setChecked(False)

        self.actionGroup.setCheckable(enabled)
        self.actionGroup.setChecked(False)

    def getSettings(self):
        conf = {}
        checkable = self.actionGroup.isCheckable()

        if not (checkable and not self.indexGroup.isChecked()):
            conf["relative"] = self.relativeCheck.isChecked()
            conf["target_index"] = self.targetIndexSpin.value()
        if not (checkable and not self.actionGroup.isChecked()):
            conf["action"] = self.actionCombo.currentData()

        return conf

    def loadSettings(self, settings):
        self._cue_index = settings.get("index", -1)

        self.relativeCheck.setChecked(settings.get("relative", True))
        self.targetIndexSpin.setValue(settings.get("target_index", 0))
        self._target_changed()  # Ensure that the correct options are displayed
        self.actionCombo.setCurrentItem(settings.get("action", ""))

    def _target_changed(self):
        target = self._current_target()

        if target is not None:
            target_class = target.__class__
        else:
            target_class = Cue

        if target_class is not self._target_class:
            self._target_class = target_class
            self.actionCombo.setItems(self._target_class.CueActions)

        self._update_suggestion()

    def _update_suggestion(self):
        target = self._current_target()

        if target is not None:
            # This require unicode support by the used font, but hey, it's 2017
            suggestion = self.actionCombo.currentText() + " ➜ " + target.name
        else:
            suggestion = IndexActionCueSettings.DEFAULT_SUGGESTION

        self.suggestionPreview.setText(suggestion)

    def _relative_changed(self):
        max_index = len(Application().cue_model) - 1

        if not self.relativeCheck.isChecked():
            self.targetIndexSpin.setRange(0, max_index)
        else:
            if self._cue_index >= 0:
                self.targetIndexSpin.setRange(
                    -self._cue_index, max_index - self._cue_index
                )
            else:
                self.targetIndexSpin.setRange(-max_index, max_index)

        self._target_changed()

    def _current_target(self):
        index = self.targetIndexSpin.value()

        if self.relativeCheck.isChecked():
            index += self._cue_index

        try:
            return Application().layout.cue_at(index)
        except IndexError:
            return None


CueSettingsRegistry().add(IndexActionCueSettings, IndexActionCue)
