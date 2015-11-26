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

from PyQt5.QtCore import QStandardPaths, Qt
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QPushButton, QLineEdit, \
    QGridLayout, QCheckBox, QSpinBox, QLabel, QFileDialog

from lisp.backends.gst.elements.uri_input import UriInput
from lisp.ui.settings.section import SettingsSection


class UriInputSettings(SettingsSection):
    NAME = 'URI Input'
    ELEMENT = UriInput

    def __init__(self, size, Id, parent=None):
        super().__init__(size, parent)

        self.id = Id

        self.groupFile = QGroupBox('Source', self)
        self.groupFile.setGeometry(0, 0, self.width(), 80)

        self.horizontalLayout = QHBoxLayout(self.groupFile)

        self.buttonFindFile = QPushButton(self.groupFile)
        self.buttonFindFile.setText('Find file')
        self.horizontalLayout.addWidget(self.buttonFindFile)

        self.filePath = QLineEdit('file://', self.groupFile)
        self.horizontalLayout.addWidget(self.filePath)

        self.groupBuffering = QGroupBox('Buffering', self)
        self.groupBuffering.setGeometry(0, 90, self.width(), 120)

        self.bufferingLayout = QGridLayout(self.groupBuffering)

        self.useBuffering = QCheckBox('Use buffering', self.groupBuffering)
        self.bufferingLayout.addWidget(self.useBuffering, 0, 0, 1, 2)

        self.download = QCheckBox(self.groupBuffering)
        self.download.setText('Attempt download on network streams')
        self.bufferingLayout.addWidget(self.download, 1, 0, 1, 2)

        self.bufferSize = QSpinBox(self.groupBuffering)
        self.bufferSize.setRange(-1, 2147483647)
        self.bufferSize.setValue(-1)
        self.bufferingLayout.addWidget(self.bufferSize, 2, 0)

        self.bufferSizeLabel = QLabel(self.groupBuffering)
        self.bufferSizeLabel.setText('Buffer size (-1 default value)')
        self.bufferSizeLabel.setAlignment(Qt.AlignCenter)
        self.bufferingLayout.addWidget(self.bufferSizeLabel, 2, 1)

        self.buttonFindFile.clicked.connect(self.select_file)

    def get_configuration(self):
        conf = {self.id: {}}

        checkable = self.groupFile.isCheckable()

        if not (checkable and not self.groupFile.isChecked()):
            conf[self.id]['uri'] = self.filePath.text()
        if not (checkable and not self.groupBuffering.isChecked()):
            conf[self.id]['use_buffing'] = self.useBuffering.isChecked()
            conf[self.id]['download'] = self.download.isChecked()
            conf[self.id]['buffer_size'] = self.bufferSize.value()

        return conf

    def set_configuration(self, conf):
        if conf is not None and self.id in conf:
            self.filePath.setText(conf[self.id]['uri'])

    def enable_check(self, enable):
        self.groupFile.setCheckable(enable)
        self.groupFile.setChecked(False)

    def select_file(self):
        path = QStandardPaths.writableLocation(QStandardPaths.MusicLocation)
        file, ok = QFileDialog.getOpenFileName(self, 'Choose file', path,
                                               'All files (*)')

        if ok:
            self.filePath.setText('file://' + file)