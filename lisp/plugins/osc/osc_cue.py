# This file is part of Linux Show Player
#
# Copyright 2019 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2016 Thomas Achtner <info@offtools.de>
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
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QGridLayout,
    QLineEdit,
    QTableView,
    QTableWidget,
    QHeaderView,
    QPushButton,
    QLabel,
    QDoubleSpinBox,
    QStyledItemDelegate,
)

from lisp.core.decorators import async_function
from lisp.core.fade_functions import FadeInType, FadeOutType
from lisp.core.fader import Fader
from lisp.core.has_properties import Property
from lisp.cues.cue import Cue, CueAction
from lisp.plugins import get_plugin
from lisp.plugins.osc.osc_server import OscMessageType
from lisp.ui.qdelegates import ComboBoxDelegate, BoolCheckBoxDelegate
from lisp.ui.qmodels import SimpleTableModel
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate
from lisp.ui.widgets import FadeComboBox

# TODO: some of this should probably be moved into the osc module

logger = logging.getLogger(__name__)


def type_can_fade(osc_type):
    if osc_type == OscMessageType.Int or osc_type == OscMessageType.Float:
        return True
    else:
        return False


class OscCue(Cue):
    Name = QT_TRANSLATE_NOOP("CueName", "OSC Cue")

    CueActions = (
        CueAction.Default,
        CueAction.Start,
        CueAction.Stop,
        CueAction.Pause,
    )

    path = Property(default="")
    args = Property(default=[])
    fade_type = Property(default=FadeInType.Linear.name)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = translate("CueName", self.Name)

        self.__osc = get_plugin("Osc")

        self.__has_fade = False
        self.__fadein = True
        self.__fader = Fader(self, "position")
        self.__position = 0

        self.changed("args").connect(self.__on_args_change)

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, value):
        self.__position = value
        args = []

        try:
            for arg in self.args:
                start = arg["start"]
                if arg["fade"]:
                    partial = (arg["end"] - start) * self.__position
                    args.append(start + partial)
                else:
                    args.append(start)

            self.__osc.server.send(self.path, *args)
        except Exception:
            self.interrupt()

            logger.exception(
                translate(
                    "OscCueError",
                    "Cannot send OSC message, see error for details",
                )
            )
            self._error()

    def __on_args_change(self, new_args):
        # Set fade type, based on the first argument that have a fade
        for arg in new_args:
            if arg["fade"]:
                self.__has_fade = True
                self.__fadein = arg["end"] > arg["start"]
                break

    def has_fade(self):
        return self.__has_fade and self.duration > 0

    def __start__(self, fade=False):
        if self.__fader.is_paused():
            self.__fader.resume()
            return True

        if self.has_fade():
            if not self.__fadein:
                self.__fade(FadeOutType[self.fade_type])
                return True
            else:
                self.__fade(FadeInType[self.fade_type])
                return True
        else:
            self.position = 1

        return False

    def __stop__(self, fade=False):
        self.__fader.stop()
        return True

    def __pause__(self, fade=False):
        self.__fader.pause()
        return True

    __interrupt__ = __stop__

    @async_function
    def __fade(self, fade_type):
        self.__position = 0
        self.__fader.prepare()
        ended = self.__fader.fade(round(self.duration / 1000, 2), 1, fade_type)

        if ended:
            # Avoid approximation problems (if needed)
            if self.position != 1:
                self.position = 1
            self._ended()

    def current_time(self):
        return self.__fader.current_time()


COL_TYPE = 0
COL_START_VALUE = 1
COL_END_VALUE = 2
COL_FADE = 3


class OscCueSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("Cue Name", "OSC Settings")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.oscGroup = QGroupBox(self)
        self.oscGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.oscGroup)

        self.pathLabel = QLabel()
        self.oscGroup.layout().addWidget(self.pathLabel, 0, 0)

        self.pathEdit = QLineEdit()
        self.oscGroup.layout().addWidget(self.pathEdit, 1, 0, 1, 2)

        self.oscModel = SimpleTableModel(
            [
                translate("OscCue", "Type"),
                translate("OscCue", "Value"),
                translate("OscCue", "FadeTo"),
                translate("OscCue", "Fade"),
            ]
        )

        self.oscView = OscView(parent=self.oscGroup)
        self.oscView.setModel(self.oscModel)
        self.oscGroup.layout().addWidget(self.oscView, 2, 0, 1, 2)

        self.addButton = QPushButton(self.oscGroup)
        self.addButton.clicked.connect(self.__new_argument)
        self.oscGroup.layout().addWidget(self.addButton, 3, 0)

        self.removeButton = QPushButton(self.oscGroup)
        self.removeButton.clicked.connect(self.__remove_argument)
        self.oscGroup.layout().addWidget(self.removeButton, 3, 1)

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

        self.pathEdit.textEdited.connect(self.__fixPath)

        self.retranslateUi()

    def __fixPath(self, text):
        # Enforce ASCII
        text = text.encode("ascii", errors="ignore").decode()
        # Enforce heading "/" to the path
        if text and text[0] != "/":
            text = "/" + text

        self.pathEdit.setText(text)

    def retranslateUi(self):
        self.oscGroup.setTitle(translate("OscCue", "OSC Message"))
        self.addButton.setText(translate("OscCue", "Add"))
        self.removeButton.setText(translate("OscCue", "Remove"))
        self.pathLabel.setText(translate("OscCue", "OSC Path:"))
        self.pathEdit.setPlaceholderText(
            translate("OscCue", "/path/to/something")
        )
        self.fadeGroup.setTitle(translate("OscCue", "Fade"))
        self.fadeLabel.setText(translate("OscCue", "Time (sec)"))
        self.fadeCurveLabel.setText(translate("OscCue", "Curve"))

    def enableCheck(self, enabled):
        self.oscGroup.setCheckable(enabled)
        self.oscGroup.setChecked(False)

        self.fadeGroup.setCheckable(enabled)
        self.fadeGroup.setChecked(False)

    def getSettings(self):
        conf = {}
        checkable = self.oscGroup.isCheckable()

        if not (checkable and not self.oscGroup.isChecked()):
            conf["path"] = self.pathEdit.text()
            conf["args"] = [
                {
                    "type": row[COL_TYPE],
                    "start": row[COL_START_VALUE],
                    "end": row[COL_END_VALUE],
                    "fade": row[COL_FADE],
                }
                for row in self.oscModel.rows
            ]

        if not (checkable and not self.fadeGroup.isCheckable()):
            conf["duration"] = self.fadeSpin.value() * 1000
            conf["fade_type"] = self.fadeCurveCombo.currentType()

        return conf

    def loadSettings(self, settings):
        self.pathEdit.setText(settings.get("path", ""))

        for arg in settings.get("args", {}):
            self.oscModel.appendRow(
                arg.get("type", "Integer"),
                arg.get("start", 0),
                arg.get("end", None),
                arg.get("fade", False),
            )

        self.fadeSpin.setValue(settings.get("duration", 0) / 1000)
        self.fadeCurveCombo.setCurrentType(settings.get("fade_type", ""))

    def __new_argument(self):
        self.oscModel.appendRow(OscMessageType.Int.value, 0, 0, False)

    def __remove_argument(self):
        if self.oscModel.rowCount():
            self.oscModel.removeRow(self.oscView.currentIndex().row())


class OscView(QTableView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.delegates = [
            ComboBoxDelegate(
                options=[i.value for i in OscMessageType],
                tr_context="OscMessageType",
            ),
            QStyledItemDelegate(),
            QStyledItemDelegate(),
            BoolCheckBoxDelegate(),
        ]

        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)

        self.setShowGrid(False)
        self.setAlternatingRowColors(True)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setHighlightSections(False)

        self.verticalHeader().sectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(24)
        self.verticalHeader().setHighlightSections(False)

        for column, delegate in enumerate(self.delegates):
            self.setItemDelegateForColumn(column, delegate)

    def setModel(self, model):
        if isinstance(model, SimpleTableModel):
            if isinstance(self.model(), SimpleTableModel):
                self.model().dataChanged.disconnect(self._dataChanged)

            super().setModel(model)
            model.dataChanged.connect(self._dataChanged)

    def _toInt(self, modelRow):
        start = modelRow[COL_START_VALUE]
        end = modelRow[COL_END_VALUE]

        modelRow[COL_END_VALUE] = 0
        modelRow[COL_START_VALUE] = 0
        # We try to covert the value, if possible
        try:
            modelRow[COL_START_VALUE] = int(start)
            modelRow[COL_END_VALUE] = int(end)
        except (ValueError, TypeError):
            pass

    def _toFloat(self, modelRow):
        start = modelRow[COL_START_VALUE]
        end = modelRow[COL_END_VALUE]

        modelRow[COL_START_VALUE] = 0.0
        modelRow[COL_END_VALUE] = 0.0
        # We try to covert the value, if possible
        # We also take care of "inf" and "-inf" values
        try:
            start = float(start)
            if float("-inf") < start < float("inf"):
                modelRow[COL_START_VALUE] = start

            end = float(end)
            if float("-inf") < end < float("inf"):
                modelRow[COL_END_VALUE] = end
        except (ValueError, TypeError):
            pass

    def _toBool(self, modelRow):
        modelRow[COL_START_VALUE] = True

    def _toString(self, modelRow):
        modelRow[COL_START_VALUE] = "text"

    def _dataChanged(self, _, bottom_right, roles):
        if Qt.EditRole not in roles:
            return

        # NOTE: We assume one item will change at the time
        column = bottom_right.column()
        modelRow = self.model().rows[bottom_right.row()]
        oscType = modelRow[COL_TYPE]

        if column == COL_TYPE:
            # Type changed, set a correct value
            # The delegate will decide the correct editor to display
            if oscType == OscMessageType.Int:
                self._toInt(modelRow)
            elif oscType == OscMessageType.Float:
                self._toFloat(modelRow)
            elif oscType == OscMessageType.Bool:
                self._toBool(modelRow)
            else:
                # We assume OscMessageType.String
                self._toString(modelRow)

        if not type_can_fade(oscType):
            # Cannot fade, keep columns cleans
            modelRow[COL_FADE] = False
            modelRow[COL_END_VALUE] = None


CueSettingsRegistry().add(OscCueSettings, OscCue)
