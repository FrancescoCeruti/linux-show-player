# This file is part of Linux Show Player
#
# Copyright 2026 Tobias Teichmann <tobias.teichmann@gmx.at>
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

import uuid
from typing import Optional

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtGui import QColor, QGuiApplication
from PyQt5.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class VideoOutputWindowsConfig(SettingsPage):
    """Manage the app-level list of named, persistent video output windows.

    Each entry (name, screen, geometry, background color) is stored under
    the "video_windows" key of the GStreamer backend configuration, and is
    picked up by `VideoOutputWindowManager` / the "Video Output Window"
    cue-element settings dropdown / the runtime "Video Outputs" menu.
    """

    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Video Output Windows")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._definitions = []
        self._current = None

        self.setLayout(QHBoxLayout())

        self.listGroup = QGroupBox(self)
        self.listGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.listGroup, 1)

        self.listWidget = QListWidget(self.listGroup)
        self.listWidget.currentItemChanged.connect(self._on_selection_changed)
        self.listGroup.layout().addWidget(self.listWidget)

        buttonsLayout = QHBoxLayout()
        self.addButton = QPushButton(self.listGroup)
        self.addButton.clicked.connect(self._add_window)
        self.removeButton = QPushButton(self.listGroup)
        self.removeButton.clicked.connect(self._remove_window)
        buttonsLayout.addWidget(self.addButton)
        buttonsLayout.addWidget(self.removeButton)
        self.listGroup.layout().addLayout(buttonsLayout)

        self.detailsGroup = QGroupBox(self)
        self.detailsGroup.setLayout(QFormLayout())
        self.detailsGroup.setEnabled(False)
        self.layout().addWidget(self.detailsGroup, 2)

        self.nameEdit = QLineEdit(self.detailsGroup)
        self.nameEdit.editingFinished.connect(self._on_name_changed)

        self.screenComboBox = QComboBox(self.detailsGroup)
        for screen in QGuiApplication.screens():
            self.screenComboBox.addItem(screen.name(), screen.name())
        self.screenComboBox.currentIndexChanged.connect(self._on_details_changed)

        self.fullscreenCheckBox = QCheckBox(self.detailsGroup)
        self.fullscreenCheckBox.toggled.connect(self._on_fullscreen_toggled)

        self.xSpinBox = QSpinBox(self.detailsGroup)
        self.xSpinBox.setRange(-10000, 10000)
        self.ySpinBox = QSpinBox(self.detailsGroup)
        self.ySpinBox.setRange(-10000, 10000)
        self.widthSpinBox = QSpinBox(self.detailsGroup)
        self.widthSpinBox.setRange(1, 10000)
        self.heightSpinBox = QSpinBox(self.detailsGroup)
        self.heightSpinBox.setRange(1, 10000)
        for spinBox in (
            self.xSpinBox,
            self.ySpinBox,
            self.widthSpinBox,
            self.heightSpinBox,
        ):
            spinBox.valueChanged.connect(self._on_details_changed)

        self.geometryWidget = QWidget(self.detailsGroup)
        geometryLayout = QHBoxLayout(self.geometryWidget)
        geometryLayout.setContentsMargins(0, 0, 0, 0)
        for label, spinBox in (
            ("x", self.xSpinBox),
            ("y", self.ySpinBox),
            ("w", self.widthSpinBox),
            ("h", self.heightSpinBox),
        ):
            geometryLayout.addWidget(QLabel(label, self.geometryWidget))
            geometryLayout.addWidget(spinBox)

        self._current_color = QColor("#000000")
        self.colorButton = QPushButton(self.detailsGroup)
        self.colorButton.clicked.connect(self._pick_color)

        self.detailsGroup.layout().addRow(
            translate("VideoOutputWindowsConfig", "Name"), self.nameEdit
        )
        self.detailsGroup.layout().addRow(
            translate("VideoOutputWindowsConfig", "Screen"), self.screenComboBox
        )
        self.detailsGroup.layout().addRow(
            translate("VideoOutputWindowsConfig", "Fullscreen"),
            self.fullscreenCheckBox,
        )
        self.detailsGroup.layout().addRow(
            translate("VideoOutputWindowsConfig", "Geometry"), self.geometryWidget
        )
        self.detailsGroup.layout().addRow(
            translate("VideoOutputWindowsConfig", "Background color"),
            self.colorButton,
        )

        self.retranslateUi()

    def retranslateUi(self) -> None:
        self.listGroup.setTitle(
            translate("VideoOutputWindowsConfig", "Output windows")
        )
        self.detailsGroup.setTitle(translate("VideoOutputWindowsConfig", "Details"))
        self.addButton.setText(translate("VideoOutputWindowsConfig", "Add"))
        self.removeButton.setText(translate("VideoOutputWindowsConfig", "Remove"))

    def loadSettings(self, settings: dict) -> None:
        self._definitions = [dict(d) for d in settings.get("video_windows", [])]

        self.listWidget.clear()
        for definition in self._definitions:
            item = QListWidgetItem(definition.get("name", definition["id"]))
            item.setData(Qt.UserRole, definition["id"])
            self.listWidget.addItem(item)

    def getSettings(self) -> dict:
        return {"video_windows": self._definitions}

    def _find(self, window_id: str) -> Optional[dict]:
        for definition in self._definitions:
            if definition["id"] == window_id:
                return definition
        return None

    def _add_window(self) -> None:
        name, ok = QInputDialog.getText(
            self,
            translate("VideoOutputWindowsConfig", "New output window"),
            translate("VideoOutputWindowsConfig", "Name"),
        )
        if not ok or not name:
            return

        primaryScreen = QGuiApplication.primaryScreen()
        definition = {
            "id": uuid.uuid4().hex,
            "name": name,
            "screen": primaryScreen.name() if primaryScreen else "",
            "fullscreen": True,
            "geometry": [0, 0, 1280, 720],
            "background_color": "#000000",
        }
        self._definitions.append(definition)

        item = QListWidgetItem(name)
        item.setData(Qt.UserRole, definition["id"])
        self.listWidget.addItem(item)
        self.listWidget.setCurrentItem(item)

    def _remove_window(self) -> None:
        item = self.listWidget.currentItem()
        if item is None:
            return

        window_id = item.data(Qt.UserRole)
        self._definitions = [d for d in self._definitions if d["id"] != window_id]
        self.listWidget.takeItem(self.listWidget.row(item))

    def _on_selection_changed(
        self, current: Optional[QListWidgetItem], previous: Optional[QListWidgetItem]
    ) -> None:
        if current is None:
            self._current = None
            self.detailsGroup.setEnabled(False)
            return

        definition = self._find(current.data(Qt.UserRole))
        if definition is None:
            return

        self._current = definition
        self.detailsGroup.setEnabled(True)

        self.nameEdit.setText(definition.get("name", ""))

        index = self.screenComboBox.findData(definition.get("screen", ""))
        self.screenComboBox.setCurrentIndex(max(index, 0))

        fullscreen = definition.get("fullscreen", True)
        self.fullscreenCheckBox.setChecked(fullscreen)
        self.geometryWidget.setEnabled(not fullscreen)

        x, y, w, h = definition.get("geometry", [0, 0, 1280, 720])
        self.xSpinBox.setValue(x)
        self.ySpinBox.setValue(y)
        self.widthSpinBox.setValue(w)
        self.heightSpinBox.setValue(h)

        self._current_color = QColor(definition.get("background_color", "#000000"))
        self._update_color_button()

    def _on_name_changed(self) -> None:
        if self._current is None:
            return

        self._current["name"] = self.nameEdit.text()

        item = self.listWidget.currentItem()
        if item is not None:
            item.setText(self._current["name"])

    def _on_fullscreen_toggled(self, checked: bool) -> None:
        if self._current is None:
            return

        self._current["fullscreen"] = checked
        self.geometryWidget.setEnabled(not checked)

    def _on_details_changed(self, *_args) -> None:
        if self._current is None:
            return

        self._current["screen"] = self.screenComboBox.currentData()
        self._current["geometry"] = [
            self.xSpinBox.value(),
            self.ySpinBox.value(),
            self.widthSpinBox.value(),
            self.heightSpinBox.value(),
        ]

    def _pick_color(self) -> None:
        color = QColorDialog.getColor(self._current_color, self)
        if not color.isValid():
            return

        self._current_color = color
        self._update_color_button()

        if self._current is not None:
            self._current["background_color"] = color.name()

    def _update_color_button(self) -> None:
        self.colorButton.setStyleSheet(
            f"background-color: {self._current_color.name()};"
        )
