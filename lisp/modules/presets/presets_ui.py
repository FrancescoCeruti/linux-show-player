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
from PyQt5.QtWidgets import QDialog, QInputDialog, QMessageBox, QListWidget, \
    QHBoxLayout, QPushButton, QVBoxLayout

from lisp.cues.cue import Cue
from lisp.cues.cue_factory import CueFactory
from lisp.modules.presets.lib import scan_presets, delete_preset, load_preset, \
    write_preset, preset_exists, rename_preset
from lisp.ui.mainwindow import MainWindow
from lisp.ui.settings.cue_settings import CueSettings
from lisp.ui.ui_utils import translate


def select_preset_dialog():
    presets = tuple(scan_presets())

    if presets:
        item, confirm = QInputDialog.getItem(
            MainWindow(),
            translate('Presets', 'Select Preset'), '',
            presets,
            editable=False)

        if confirm:
            return item
    else:
        QMessageBox.warning(
            MainWindow(),
            translate('Presets', 'Warning'),
            translate('Presets', 'No preset found!'))


def save_preset_dialog():
    name, confirm = QInputDialog.getText(
        MainWindow(),
        translate('Presets', 'Presets'),
        translate('Presets', 'Preset name'))

    if confirm:
        if preset_exists(name):
            answer = QMessageBox.question(
                MainWindow(),
                translate('Presets', 'Presets'),
                translate('Presets', 'Preset already exists, overwrite?'),
                buttons=QMessageBox.Yes | QMessageBox.Cancel)

            if answer == QMessageBox.Yes:
                return name
        else:
            return name


class PresetsUi(QDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resize(400, 400)
        self.setMaximumSize(self.size())
        self.setMinimumSize(self.size())
        self.setLayout(QVBoxLayout())
        self.setWindowModality(Qt.ApplicationModal)

        self.presetsList = QListWidget(self)
        self.presetsList.setAlternatingRowColors(True)
        self.presetsList.setFocusPolicy(Qt.NoFocus)
        self.presetsList.addItems(scan_presets())
        self.presetsList.setSortingEnabled(True)
        self.presetsList.itemSelectionChanged.connect(self.__selection_changed)
        self.presetsList.itemDoubleClicked.connect(self.__rename_preset)
        self.layout().addWidget(self.presetsList)

        self.buttonsLayout = QHBoxLayout()
        self.buttonsLayout.setAlignment(Qt.AlignRight)
        self.layout().addLayout(self.buttonsLayout)

        self.addPresetButton = QPushButton(self)
        self.addPresetButton.clicked.connect(self.__add_preset)

        self.editPresetButton = QPushButton(self)
        self.editPresetButton.clicked.connect(self.__edit_preset)

        self.removePresetButton = QPushButton(self)
        self.removePresetButton.clicked.connect(self.__remove_preset)

        self.buttonsLayout.addWidget(self.addPresetButton)
        self.buttonsLayout.addWidget(self.editPresetButton)
        self.buttonsLayout.addWidget(self.removePresetButton)

        self.retranslateUi()

    def retranslateUi(self):
        self.addPresetButton.setText(translate('Presets', 'Add'))
        self.editPresetButton.setText(translate('Presets', 'Edit'))
        self.removePresetButton.setText(translate('Presets', 'Remove'))

    def __remove_preset(self):
        item = self.presetsList.currentItem()
        if item is not None:
            if delete_preset(item.text()):
                self.presetsList.takeItem(self.presetsList.currentRow())

    def __add_preset(self):
        name = save_preset_dialog()
        if name is not None:
            if write_preset(name, {'_type_': 'Cue'}):
                self.presetsList.addItem(name)

    def __rename_preset(self, item):
        new_name = save_preset_dialog()
        if new_name is not None:
            if rename_preset(item.text(), new_name):
                item.setText(new_name)

    def __edit_preset(self):
        item = self.presetsList.currentItem()
        if item:
            preset = load_preset(item.text())

            try:
                cue_class = CueFactory.create_cue(preset.get('_type_'))
                cue_class = cue_class.__class__
            except Exception:
                cue_class = Cue

            edit_dialog = CueSettings(cue_class=cue_class)
            edit_dialog.load_settings(preset)
            if edit_dialog.exec_() == edit_dialog.Accepted:
                write_preset(item.text(), edit_dialog.get_settings())

    def __selection_changed(self):
        selection = bool(self.presetsList.selectedIndexes())

        self.editPresetButton.setEnabled(selection)
        self.removePresetButton.setEnabled(selection)
