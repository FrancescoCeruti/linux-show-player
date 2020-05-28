# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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


import ast
import logging

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import (
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QTableView,
    QTableWidget,
    QHeaderView,
    QGridLayout,
    QLabel,
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QMessageBox,
    QSpacerItem,
)

from lisp.plugins import get_plugin, PluginNotLoadedError
from lisp.plugins.controller.common import LayoutAction, tr_layout_action
from lisp.plugins.controller.protocol import Protocol
from lisp.plugins.osc.osc_delegate import OscArgumentDelegate
from lisp.plugins.osc.osc_server import OscMessageType
from lisp.ui.qdelegates import (
    ComboBoxDelegate,
    CueActionDelegate,
    EnumComboBoxDelegate,
    LabelDelegate,
)
from lisp.ui.qmodels import SimpleTableModel
from lisp.ui.settings.pages import SettingsPage, CuePageMixin
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class OscMessageDialog(QDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QGridLayout())
        self.setMinimumSize(500, 300)
        self.resize(500, 350)

        self.pathLabel = QLabel(self)
        self.layout().addWidget(self.pathLabel, 0, 0, 1, 2)

        self.pathEdit = QLineEdit(self)
        self.layout().addWidget(self.pathEdit, 1, 0, 1, 2)

        self.model = SimpleTableModel(
            [translate("Osc Cue", "Type"), translate("Osc Cue", "Argument")]
        )
        self.model.dataChanged.connect(self.__argumentChanged)

        self.view = OscArgumentView(parent=self)
        self.view.setModel(self.model)
        self.layout().addWidget(self.view, 2, 0, 1, 2)

        self.addButton = QPushButton(self)
        self.addButton.clicked.connect(self.__addArgument)
        self.layout().addWidget(self.addButton, 3, 0)

        self.removeButton = QPushButton(self)
        self.removeButton.clicked.connect(self.__removeArgument)
        self.layout().addWidget(self.removeButton, 3, 1)

        self.layout().addItem(QSpacerItem(0, 20), 4, 0, 1, 2)

        self.buttons = QDialogButtonBox(self)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        self.buttons.addButton(QDialogButtonBox.Ok)
        self.layout().addWidget(self.buttons, 5, 0, 1, 2)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(translate("ControllerOscSettings", "OSC Message"))
        self.pathLabel.setText(translate("ControllerOscSettings", "OSC Path:",))
        self.pathEdit.setPlaceholderText(
            translate("ControllerOscSettings", "/path/to/method")
        )
        self.addButton.setText(translate("OscCue", "Add"))
        self.removeButton.setText(translate("OscCue", "Remove"))

    def getMessage(self):
        path = self.pathEdit.text()
        types = ""
        arguments = []

        for rowType, rowValue in self.model.rows:
            if rowType == OscMessageType.Bool:
                types += "T" if rowValue else "F"
            else:
                if rowType == OscMessageType.Int:
                    types += "i"
                elif rowType == OscMessageType.Float:
                    types += "f"
                elif rowType == OscMessageType.String:
                    types += "s"
                else:
                    raise TypeError("Unsupported Osc Type")

                arguments.append(rowValue)

        return path, types, str(arguments)[1:-1]

    def setMessage(self, path, types, arguments):
        self.pathEdit.setText(path)
        # Split strings
        types = tuple(types)
        arguments = ast.literal_eval(f"[{arguments}]")

        # We keep a separate index, because booleans don't have a value
        valIndex = 0
        for t in types:
            if t == "T" or t == "F":
                rowType = OscMessageType.Bool.value
                rowValue = t == "T"
            elif valIndex < len(arguments):
                if t == "i":
                    rowType = OscMessageType.Int.value
                    rowValue = self.__castValue(arguments[valIndex], int, 0)
                elif t == "f":
                    rowType = OscMessageType.Float.value
                    rowValue = self.__castValue(arguments[valIndex], float, 0.0)
                elif t == "s":
                    rowType = OscMessageType.String.value
                    rowValue = arguments[valIndex]
                else:
                    valIndex += 1
                    continue

                valIndex += 1
            else:
                continue

            self.model.appendRow(rowType, rowValue)

    def __addArgument(self):
        self.model.appendRow(OscMessageType.Int.value, 0)

    def __removeArgument(self):
        if self.model.rowCount() and self.view.currentIndex().row() > -1:
            self.model.removeRow(self.view.currentIndex().row())

    def __argumentChanged(self, topLeft, bottomRight, roles):
        # If the "Type" column has changed
        if Qt.EditRole in roles and bottomRight.column() == 0:
            # Get the edited row
            row = self.model.rows[topLeft.row()]
            oscType = row[0]

            # Update the value column with a proper type
            if oscType == OscMessageType.Int:
                row[1] = self.__castValue(row[1], int, 0)
            elif oscType == OscMessageType.Float:
                row[1] = self.__castValue(row[1], float, 0.0)
            elif oscType == OscMessageType.Bool:
                row[1] = True
            else:
                row[1] = ""

    def __castValue(self, value, toType, default):
        try:
            return toType(value)
        except (TypeError, ValueError):
            return default


class OscArgumentView(QTableView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.delegates = [
            ComboBoxDelegate(
                options=[i.value for i in OscMessageType],
                tr_context="OscMessageType",
            ),
            OscArgumentDelegate(),
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


class OscSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "OSC Controls")

    def __init__(self, actionDelegate, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.oscGroup = QGroupBox(self)
        self.oscGroup.setTitle(translate("ControllerOscSettings", "OSC"))
        self.oscGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.oscGroup)

        self.oscModel = OscModel()

        self.OscView = OscView(actionDelegate, parent=self.oscGroup)
        self.OscView.setModel(self.oscModel)
        self.oscGroup.layout().addWidget(self.OscView, 0, 0, 1, 2)

        self.addButton = QPushButton(self.oscGroup)
        self.addButton.clicked.connect(self.__new_message)
        self.oscGroup.layout().addWidget(self.addButton, 1, 0)

        self.removeButton = QPushButton(self.oscGroup)
        self.removeButton.clicked.connect(self.__remove_message)
        self.oscGroup.layout().addWidget(self.removeButton, 1, 1)

        self.oscCapture = QPushButton(self.oscGroup)
        self.oscCapture.clicked.connect(self.capture_message)
        self.oscGroup.layout().addWidget(self.oscCapture, 2, 0)

        self.captureDialog = QDialog(self, flags=Qt.Dialog)
        self.captureDialog.resize(300, 150)
        self.captureDialog.setMaximumSize(self.captureDialog.size())
        self.captureDialog.setMinimumSize(self.captureDialog.size())
        self.captureDialog.setWindowTitle(
            translate("ControllerOscSettings", "OSC Capture")
        )
        self.captureDialog.setModal(True)
        self.captureLabel = QLabel("Waiting for message:")
        self.captureLabel.setAlignment(Qt.AlignCenter)
        self.captureDialog.setLayout(QVBoxLayout())
        self.captureDialog.layout().addWidget(self.captureLabel)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self.captureDialog,
        )
        self.buttonBox.accepted.connect(self.captureDialog.accept)
        self.buttonBox.rejected.connect(self.captureDialog.reject)
        self.captureDialog.layout().addWidget(self.buttonBox)

        self.capturedMessage = {"path": None, "types": None, "args": None}

        self.retranslateUi()

        self._defaultAction = None
        try:
            self.__osc = get_plugin("Osc")
        except PluginNotLoadedError:
            self.setEnabled(False)

    def retranslateUi(self):
        self.addButton.setText(translate("ControllerOscSettings", "Add"))
        self.removeButton.setText(translate("ControllerOscSettings", "Remove"))
        self.oscCapture.setText(translate("ControllerOscSettings", "Capture"))

    def enableCheck(self, enabled):
        self.oscGroup.setCheckable(enabled)
        self.oscGroup.setChecked(False)

    def getSettings(self):
        entries = []
        for row in self.oscModel.rows:
            message = Osc.key_from_values(row[0], row[1], row[2])
            entries.append((message, row[3]))

        return {"osc": entries}

    def loadSettings(self, settings):
        for entry in settings.get("osc", ()):
            try:
                message = Osc.message_from_key(entry[0])
                self.oscModel.appendRow(
                    message[0], message[1], str(message[2:])[1:-1], entry[1]
                )
            except Exception:
                logger.warning(
                    translate(
                        "ControllerOscSettingsWarning",
                        "Error while importing configuration entry, skipped.",
                    ),
                    exc_info=True,
                )

    def capture_message(self):
        self.__osc.server.new_message.connect(self.__show_message)

        result = self.captureDialog.exec()
        if result == QDialog.Accepted and self.capturedMessage["path"]:
            args = str(self.capturedMessage["args"])[1:-1]
            self.oscModel.appendRow(
                self.capturedMessage["path"],
                self.capturedMessage["types"],
                args,
                self._defaultAction,
            )

        self.__osc.server.new_message.disconnect(self.__show_message)

        self.captureLabel.setText(
            translate("ControllerOscSettings", "Waiting for messages:")
        )

    def __show_message(self, path, args, types, *_, **__):
        self.capturedMessage["path"] = path
        self.capturedMessage["types"] = types
        self.capturedMessage["args"] = args
        self.captureLabel.setText(f'OSC: "{path}" "{types}" {args}')

    def __new_message(self):
        dialog = OscMessageDialog(parent=self)
        if dialog.exec() == dialog.Accepted:
            path, types, arguments = dialog.getMessage()

            if len(path) < 2 or path[0] != "/":
                QMessageBox.warning(
                    self,
                    translate("ControllerOscSettingsWarning", "Warning"),
                    translate(
                        "ControllerOscSettingsWarning",
                        "Osc path seems invalid,\n"
                        "do not forget to edit the path later.",
                    ),
                )

            self.oscModel.appendRow(path, types, arguments, self._defaultAction)

    def __remove_message(self):
        if self.oscModel.rowCount() and self.OscView.currentIndex().row() > -1:
            self.oscModel.removeRow(self.OscView.currentIndex().row())


class OscCueSettings(OscSettings, CuePageMixin):
    def __init__(self, cueType, **kwargs):
        super().__init__(
            actionDelegate=CueActionDelegate(
                cue_class=cueType, mode=CueActionDelegate.Mode.Name
            ),
            cueType=cueType,
            **kwargs,
        )
        self._defaultAction = self.cueType.CueActions[0].name


class OscLayoutSettings(OscSettings):
    def __init__(self, **kwargs):
        super().__init__(
            actionDelegate=EnumComboBoxDelegate(
                LayoutAction,
                mode=EnumComboBoxDelegate.Mode.Name,
                trItem=tr_layout_action,
            ),
            **kwargs,
        )
        self._defaultAction = LayoutAction.Go.name


class OscView(QTableView):
    def __init__(self, actionDelegate, **kwargs):
        super().__init__(**kwargs)

        self.delegates = [
            LabelDelegate(),
            LabelDelegate(),
            LabelDelegate(),
            actionDelegate,
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

        self.doubleClicked.connect(self.__doubleClicked)

    def __doubleClicked(self, index):
        if index.column() <= 2:
            row = self.model().rows[index.row()]
            dialog = OscMessageDialog()
            dialog.setMessage(row[0], row[1], row[2])

            if dialog.exec() == dialog.Accepted:
                path, types, arguments = dialog.getMessage()
                self.model().updateRow(
                    index.row(), path, types, arguments, row[3]
                )


class OscModel(SimpleTableModel):
    def __init__(self):
        super().__init__(
            [
                translate("ControllerOscSettings", "Path"),
                translate("ControllerOscSettings", "Types"),
                translate("ControllerOscSettings", "Arguments"),
                translate("ControllerOscSettings", "Action"),
            ]
        )

    def flags(self, index):
        if index.column() <= 2:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

        return super().flags(index)


class Osc(Protocol):
    CueSettings = OscCueSettings
    LayoutSettings = OscLayoutSettings

    def __init__(self):
        super().__init__()

        osc = get_plugin("Osc")
        osc.server.new_message.connect(self.__new_message)

    def __new_message(self, path, args, types, *_, **__):
        key = self.key_from_message(path, types, args)
        self.protocol_event.emit(key)

    @staticmethod
    def key_from_message(path, types, args):
        return f"OSC{[path, types, *args]}"

    @staticmethod
    def key_from_values(path, types, args):
        if not types:
            return f"OSC['{path}', '{types}']"
        else:
            return f"OSC['{path}', '{types}', {args}]"

    @staticmethod
    def message_from_key(key):
        return ast.literal_eval(key[3:])
