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

from typing import Optional, TYPE_CHECKING

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QVBoxLayout,
)

from lisp import backend
from lisp.plugins.gst_backend.elements.video_output import VideoOutput
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate

if TYPE_CHECKING:
    from lisp.plugins.gst_backend.video_output.manager import (
        VideoOutputWindowManager,
    )


class VideoOutputSettings(SettingsPage):
    ELEMENT = VideoOutput
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.windowGroup = QGroupBox(self)
        self.windowGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.windowGroup)

        self.windowComboBox = QComboBox(self.windowGroup)
        self.windowGroup.layout().addWidget(self.windowComboBox)

        self.positionGroup = QGroupBox(self)
        self.positionGroup.setLayout(QFormLayout())
        self.layout().addWidget(self.positionGroup)

        self.xSpinBox = QDoubleSpinBox(self.positionGroup)
        self.xSpinBox.setRange(0, 100)
        self.xSpinBox.setSuffix(" %")
        self.ySpinBox = QDoubleSpinBox(self.positionGroup)
        self.ySpinBox.setRange(0, 100)
        self.ySpinBox.setSuffix(" %")
        self.widthSpinBox = QDoubleSpinBox(self.positionGroup)
        self.widthSpinBox.setRange(1, 100)
        self.widthSpinBox.setSuffix(" %")
        self.heightSpinBox = QDoubleSpinBox(self.positionGroup)
        self.heightSpinBox.setRange(1, 100)
        self.heightSpinBox.setSuffix(" %")

        self.positionGroup.layout().addRow("X", self.xSpinBox)
        self.positionGroup.layout().addRow("Y", self.ySpinBox)
        self.positionGroup.layout().addRow("Width", self.widthSpinBox)
        self.positionGroup.layout().addRow("Height", self.heightSpinBox)

        self._populate()
        self.retranslateUi()

    @staticmethod
    def _manager() -> Optional["VideoOutputWindowManager"]:
        gst_backend = backend.get_backend()
        return getattr(gst_backend, "video_outputs", None)

    def _populate(self) -> None:
        self.windowComboBox.clear()

        manager = self._manager()
        for window_id, name in manager.list_windows() if manager else []:
            self.windowComboBox.addItem(name, (window_id, name, True))  # (id, name, resolved)

    def retranslateUi(self) -> None:
        self.windowGroup.setTitle(
            translate("VideoOutputSettings", "Output window")
        )
        self.positionGroup.setTitle(
            translate("VideoOutputSettings", "Position & Size")
        )
        self.positionGroup.layout().labelForField(self.xSpinBox).setText(
            translate("VideoOutputSettings", "X")
        )
        self.positionGroup.layout().labelForField(self.ySpinBox).setText(
            translate("VideoOutputSettings", "Y")
        )
        self.positionGroup.layout().labelForField(self.widthSpinBox).setText(
            translate("VideoOutputSettings", "Width")
        )
        self.positionGroup.layout().labelForField(self.heightSpinBox).setText(
            translate("VideoOutputSettings", "Height")
        )

    def enableCheck(self, enabled: bool) -> None:
        self.setGroupEnabled(self.windowGroup, enabled)
        self.setGroupEnabled(self.positionGroup, enabled)

    def loadSettings(self, settings: dict) -> None:
        self._populate()

        self.xSpinBox.setValue(settings.get("pos_x", 0.0) * 100)
        self.ySpinBox.setValue(settings.get("pos_y", 0.0) * 100)
        self.widthSpinBox.setValue(settings.get("scale_width", 1.0) * 100)
        self.heightSpinBox.setValue(settings.get("scale_height", 1.0) * 100)

        window_id = settings.get("window_id", "")
        window_name = settings.get("window_name", "")

        index = -1
        for i in range(self.windowComboBox.count()):
            item_id, item_name, _ = self.windowComboBox.itemData(i)
            if window_id and item_id == window_id:
                index = i
                break
        if index < 0 and window_name:
            for i in range(self.windowComboBox.count()):
                item_id, item_name, _ = self.windowComboBox.itemData(i)
                if item_name == window_name:
                    index = i
                    break

        if index < 0 and (window_id or window_name):
            label = translate(
                "VideoOutputSettings", "{} (unavailable)"
            ).format(window_name or window_id)
            self.windowComboBox.insertItem(
                0, label, (window_id, window_name, False)
            )
            index = 0

        if index >= 0:
            self.windowComboBox.setCurrentIndex(index)

    def getSettings(self) -> dict:
        settings = {}

        if self.isGroupEnabled(self.windowGroup):
            data = self.windowComboBox.currentData()
            if data is None:
                settings["window_id"] = ""
                settings["window_name"] = ""
            else:
                window_id, window_name, _ = data
                settings["window_id"] = window_id
                settings["window_name"] = window_name

        if self.isGroupEnabled(self.positionGroup):
            settings["pos_x"] = self.xSpinBox.value() / 100
            settings["pos_y"] = self.ySpinBox.value() / 100
            settings["scale_width"] = self.widthSpinBox.value() / 100
            settings["scale_height"] = self.heightSpinBox.value() / 100

        return settings
