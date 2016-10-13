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
    QPushButton, QVBoxLayout, QGridLayout, QDialogButtonBox, QWidget

from lisp.cues.cue import Cue
from lisp.cues.cue_factory import CueFactory
from lisp.modules.presets.lib import scan_presets, delete_preset, load_preset, \
    write_preset, preset_exists, rename_preset
from lisp.ui.mainwindow import MainWindow
from lisp.ui.settings.cue_settings import CueSettings, CueSettingsRegistry
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


class PresetsDialog(QDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resize(500, 400)
        self.setMaximumSize(self.size())
        self.setMinimumSize(self.size())
        self.setLayout(QGridLayout())
        self.setWindowModality(Qt.ApplicationModal)

        self.presetsList = QListWidget(self)
        self.presetsList.setAlternatingRowColors(True)
        self.presetsList.setFocusPolicy(Qt.NoFocus)
        self.presetsList.addItems(scan_presets())
        self.presetsList.setSortingEnabled(True)
        self.presetsList.itemSelectionChanged.connect(self.__selection_changed)
        self.presetsList.itemDoubleClicked.connect(self.__edit_preset)
        self.layout().addWidget(self.presetsList, 0, 0)

        self.presetsButtons = QWidget(self)
        self.presetsButtons.setLayout(QVBoxLayout())
        self.presetsButtons.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.presetsButtons, 0, 1)
        self.layout().setAlignment(self.presetsButtons, Qt.AlignTop)

        self.addPresetButton = QPushButton(self.presetsButtons)
        self.addPresetButton.clicked.connect(self.__add_preset)
        self.presetsButtons.layout().addWidget(self.addPresetButton)

        self.renamePresetButton = QPushButton(self.presetsButtons)
        self.renamePresetButton.clicked.connect(self.__rename_preset)
        self.presetsButtons.layout().addWidget(self.renamePresetButton)

        self.editPresetButton = QPushButton(self.presetsButtons)
        self.editPresetButton.clicked.connect(self.__edit_preset)
        self.presetsButtons.layout().addWidget(self.editPresetButton)

        self.removePresetButton = QPushButton(self.presetsButtons)
        self.removePresetButton.clicked.connect(self.__remove_preset)
        self.presetsButtons.layout().addWidget(self.removePresetButton)

        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setStandardButtons(QDialogButtonBox.Ok)
        self.dialogButtons.accepted.connect(self.accept)
        self.layout().addWidget(self.dialogButtons, 1, 0, 1, 2)

        self.layout().setColumnStretch(0, 4)
        self.layout().setColumnStretch(1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.addPresetButton.setText(translate('Presets', 'Add'))
        self.renamePresetButton.setText(translate('Presets', 'Rename'))
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
            types = [c.__name__ for c in CueSettingsRegistry().ref_classes()]
            cue_type, confirm = QInputDialog.getItem(
                self,
                translate('Presets', 'Presets'),
                translate('Presets', 'Select cue type:'),
                types)

            if confirm:
                if write_preset(name, {'_type_': cue_type}):
                    self.presetsList.addItem(name)

    def __rename_preset(self):
        item = self.presetsList.currentItem()
        if item is not None:
            new_name = save_preset_dialog()
            if new_name is not None:
                if rename_preset(item.text(), new_name):
                    item.setText(new_name)

    def __edit_preset(self, *args):
        item = self.presetsList.currentItem()
        if item is not None:
            preset = load_preset(item.text())

            try:
                cue_class = CueFactory.create_cue(preset.get('_type_'))
                cue_class = cue_class.__class__
            except Exception:
                cue_class = Cue

            edit_dialog = CueSettings(cue_class=cue_class)
            edit_dialog.load_settings(preset)
            if edit_dialog.exec_() == edit_dialog.Accepted:
                preset.update(edit_dialog.get_settings())
                write_preset(item.text(), preset)

    def __selection_changed(self):
        selection = bool(self.presetsList.selectedIndexes())

        self.editPresetButton.setEnabled(selection)
        self.removePresetButton.setEnabled(selection)
