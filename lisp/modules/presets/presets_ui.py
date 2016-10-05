# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QInputDialog, QMessageBox, QListWidget
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout

from lisp.ui.mainwindow import MainWindow
from lisp.ui.ui_utils import translate


def select_preset_dialog(presets):
    if not presets:
        QMessageBox.warning(MainWindow(),
                            translate('Preset', 'Warning'),
                            translate('Preset', 'No preset found!'))
        return

    item, ok = QInputDialog.getItem(MainWindow(),
                                    translate('Presets', 'Select Preset'), '',
                                    presets, editable=False)

    return item if ok else None


class PresetsUi(QDialog):

    def __init__(self, presets, **kwargs):
        super().__init__(**kwargs)
        self.resize(400, 400)
        self.setMaximumSize(self.size())
        self.setMinimumSize(self.size())
        self.setLayout(QVBoxLayout())

        self.presetsList = QListWidget(self)
        self.presetsList.addItems(presets)
        self.layout().addWidget(self.presetsList)

        self.buttonsLayout = QHBoxLayout()
        self.buttonsLayout.setAlignment(Qt.AlignRight)
        self.layout().addLayout(self.buttonsLayout)

        self.addPresetButton = QPushButton(self)
        self.editPresetButton = QPushButton(self)
        self.removePresetButton = QPushButton(self)

        self.buttonsLayout.addWidget(self.addPresetButton)
        self.buttonsLayout.addWidget(self.editPresetButton)
        self.buttonsLayout.addWidget(self.removePresetButton)

        self.retranslateUi()

    def retranslateUi(self):
        self.addPresetButton.setText(translate('Preset', 'Add'))
        self.editPresetButton.setText(translate('Preset', 'Edit'))
        self.removePresetButton.setText(translate('Preset', 'Remove'))
