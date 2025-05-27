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

import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QGridLayout,
    QCheckBox,
    QSpinBox,
    QLabel,
    QFileDialog,
    QVBoxLayout,
)

from lisp.application import Application
from lisp.core.session_uri import SessionURI
from lisp.plugins.gst_backend import GstBackend
from lisp.plugins.gst_backend.elements.uri_input import UriInput
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class UriInputSettings(SettingsPage):
    ELEMENT = UriInput
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        self.fileGroup = QGroupBox(self)
        self.fileGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.fileGroup)

        self.buttonFindFile = QPushButton(self.fileGroup)
        self.fileGroup.layout().addWidget(self.buttonFindFile)

        self.filePath = QLineEdit("file://", self.fileGroup)
        self.fileGroup.layout().addWidget(self.filePath)

        self.bufferingGroup = QGroupBox(self)
        self.bufferingGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.bufferingGroup)

        self.useBuffering = QCheckBox(self.bufferingGroup)
        self.bufferingGroup.layout().addWidget(self.useBuffering, 0, 0, 1, 2)

        self.download = QCheckBox(self.bufferingGroup)
        self.bufferingGroup.layout().addWidget(self.download, 1, 0, 1, 2)

        self.bufferSize = QSpinBox(self.bufferingGroup)
        self.bufferSize.setRange(-1, 2_147_483_647)
        self.bufferSize.setValue(-1)
        self.bufferingGroup.layout().addWidget(self.bufferSize, 2, 0)

        self.bufferSizeLabel = QLabel(self.bufferingGroup)
        self.bufferSizeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bufferingGroup.layout().addWidget(self.bufferSizeLabel, 2, 1)

        self.buttonFindFile.clicked.connect(self.select_file)

        self.retranslateUi()

    def retranslateUi(self):
        self.fileGroup.setTitle(translate("UriInputSettings", "Source"))
        self.buttonFindFile.setText(translate("UriInputSettings", "Find File"))
        self.bufferingGroup.setTitle(translate("UriInputSettings", "Buffering"))
        self.useBuffering.setText(
            translate("UriInputSettings", "Use Buffering")
        )
        self.download.setText(
            translate("UriInputSettings", "Attempt download on network streams")
        )
        self.bufferSizeLabel.setText(
            translate("UriInputSettings", "Buffer size (-1 default value)")
        )

    def getSettings(self):
        settings = {}

        if self.isGroupEnabled(self.fileGroup):
            settings["uri"] = self.filePath.text()
        if self.isGroupEnabled(self.bufferingGroup):
            settings["use_buffering"] = self.useBuffering.isChecked()
            settings["download"] = self.download.isChecked()
            settings["buffer_size"] = self.bufferSize.value()

        return settings

    def loadSettings(self, settings):
        self.filePath.setText(settings.get("uri", ""))
        self.useBuffering.setChecked(settings.get("use_buffering", False))
        self.download.setChecked(settings.get("download", False))
        self.bufferSize.setValue(settings.get("buffer_size", -1))

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.fileGroup, enabled)

    def select_file(self):
        directory = ""
        current = SessionURI(self.filePath.text())

        if current.is_local:
            directory = current.absolute_path
        if not os.path.exists(directory):
            directory = GstBackend.Config.get("mediaLookupDir", "")
        if not os.path.exists(directory):
            directory = Application().session.dir()

        path, _ = QFileDialog.getOpenFileName(
            self,
            translate("UriInputSettings", "Choose file"),
            directory,
            translate("UriInputSettings", "All files") + " (*)",
        )

        if os.path.exists(path):
            self.filePath.setText(Application().session.rel_path(path))
