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
    write_preset
from lisp.ui.mainwindow import MainWindow
from lisp.ui.settings.cue_settings import CueSettings
from lisp.ui.ui_utils import translate


def select_preset_dialog():
    presets = tuple(scan_presets())

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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resize(400, 400)
        self.setMaximumSize(self.size())
        self.setMinimumSize(self.size())
        self.setLayout(QVBoxLayout())

        self.presetsList = QListWidget(self)
        self.presetsList.setAlternatingRowColors(True)
        self.presetsList.setFocusPolicy(Qt.NoFocus)
        self.presetsList.addItems(scan_presets())
        self.presetsList.itemSelectionChanged.connect(self.__selection_changed)
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
        self.addPresetButton.setText(translate('Preset', 'Add'))
        self.editPresetButton.setText(translate('Preset', 'Edit'))
        self.removePresetButton.setText(translate('Preset', 'Remove'))

    def __remove_preset(self):
        item = self.presetsList.currentItem()
        if item:
            delete_preset(item.text())

    def __add_preset(self):
        name = 'TEST'
        write_preset(name, {'_type_': 'Cue'})

        self.presetsList.addItem(name)

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
