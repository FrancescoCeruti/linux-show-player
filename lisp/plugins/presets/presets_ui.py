# This file is part of Linux Show Player
#
# Copyright 2019 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QInputDialog,
    QMessageBox,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QDialogButtonBox,
    QWidget,
    QLabel,
    QLineEdit,
    QFileDialog,
    QHBoxLayout,
)
from zipfile import BadZipFile

from lisp.core.util import natural_keys
from lisp.cues.cue import Cue
from lisp.cues.cue_factory import CueFactory
from lisp.plugins.presets.lib import (
    preset_exists,
    export_presets,
    import_presets,
    import_has_conflicts,
    scan_presets,
    delete_preset,
    write_preset,
    rename_preset,
    load_preset,
    load_on_cues,
)
from lisp.ui.mainwindow import MainWindow
from lisp.ui.settings.cue_settings import CueSettingsDialog, CueSettingsRegistry
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__file__[:-3])


def preset_error(exception, text):
    logger.error(text, exc_info=exception)


def scan_presets_error(exception):
    preset_error(exception, translate("Presets", "Cannot scan presets"))


def delete_preset_error(exception, name):
    preset_error(
        exception,
        translate("Presets", 'Error while deleting preset "{}"').format(name),
    )


def load_preset_error(exception, name):
    preset_error(
        exception, translate("Presets", 'Cannot load preset "{}"').format(name)
    )


def write_preset_error(exception, name):
    preset_error(
        exception, translate("Presets", 'Cannot save preset "{}"').format(name)
    )


def rename_preset_error(exception, name):
    preset_error(
        exception,
        translate("Presets", 'Cannot rename preset "{}"').format(name),
    )


def select_preset_dialog():
    try:
        presets = tuple(sorted(scan_presets(), key=natural_keys))

        if presets:
            item, confirm = QInputDialog.getItem(
                MainWindow(), translate("Presets", "Select Preset"), "", presets
            )

            if confirm:
                return item
    except OSError as e:
        scan_presets_error(e)


def check_override_dialog(preset_name):
    answer = QMessageBox.question(
        MainWindow(),
        translate("Presets", "Presets"),
        translate(
            "Presets",
            'Preset "{}" already exists, overwrite?'.format(preset_name),
        ),
        buttons=QMessageBox.Yes | QMessageBox.Cancel,
    )

    return answer == QMessageBox.Yes


def save_preset_dialog(base_name=""):
    name, confirm = QInputDialog.getText(
        MainWindow(),
        translate("Presets", "Presets"),
        translate("Presets", "Preset name"),
        text=base_name,
    )

    if confirm:
        return name


class PresetsDialog(QDialog):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        self.resize(500, 400)
        self.setMaximumSize(self.size())
        self.setMinimumSize(self.size())
        self.setModal(True)
        self.setLayout(QGridLayout())

        # TODO: natural sorting (QStringListModel + QListView + ProxyModel)
        self.presetsList = QListWidget(self)
        self.presetsList.setAlternatingRowColors(True)
        self.presetsList.setFocusPolicy(Qt.NoFocus)
        self.presetsList.setSortingEnabled(True)
        self.presetsList.setSelectionMode(QListWidget.ExtendedSelection)
        self.presetsList.itemSelectionChanged.connect(self.__selection_changed)
        self.presetsList.itemDoubleClicked.connect(self.__edit_preset)
        self.layout().addWidget(self.presetsList, 0, 0)

        # Preset buttons
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

        self.cueFromSelectedButton = QPushButton(self.presetsButtons)
        self.cueFromSelectedButton.clicked.connect(self.__cue_from_selected)
        self.presetsButtons.layout().addWidget(self.cueFromSelectedButton)

        self.loadOnSelectedButton = QPushButton(self.presetsButtons)
        self.loadOnSelectedButton.clicked.connect(self.__load_on_selected)
        self.presetsButtons.layout().addWidget(self.loadOnSelectedButton)

        # Import/Export buttons
        self.ieButtons = QWidget(self)
        self.ieButtons.setLayout(QHBoxLayout())
        self.ieButtons.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.ieButtons, 1, 0)
        self.layout().setAlignment(self.ieButtons, Qt.AlignLeft)

        self.exportSelectedButton = QPushButton(self.ieButtons)
        self.exportSelectedButton.clicked.connect(self.__export_presets)
        self.ieButtons.layout().addWidget(self.exportSelectedButton)

        self.importButton = QPushButton(self.ieButtons)
        self.importButton.clicked.connect(self.__import_presets)
        self.ieButtons.layout().addWidget(self.importButton)

        # Dialog buttons
        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setStandardButtons(QDialogButtonBox.Ok)
        self.dialogButtons.accepted.connect(self.accept)
        self.layout().addWidget(self.dialogButtons, 1, 1)

        self.layout().setColumnStretch(0, 4)
        self.layout().setColumnStretch(1, 1)

        self.retranslateUi()

        self.__populate()
        self.__selection_changed()

    def retranslateUi(self):
        self.addPresetButton.setText(translate("Presets", "Add"))
        self.renamePresetButton.setText(translate("Presets", "Rename"))
        self.editPresetButton.setText(translate("Presets", "Edit"))
        self.removePresetButton.setText(translate("Presets", "Remove"))
        self.cueFromSelectedButton.setText(translate("Preset", "Create Cue"))
        self.loadOnSelectedButton.setText(
            translate("Preset", "Load on selected Cues")
        )
        self.exportSelectedButton.setText(
            translate("Presets", "Export selected")
        )
        self.importButton.setText(translate("Presets", "Import"))

    def __populate(self):
        self.presetsList.clear()
        try:
            self.presetsList.addItems(scan_presets())
        except OSError as e:
            scan_presets_error(e)

    def __remove_preset(self):
        for item in self.presetsList.selectedItems():
            try:
                delete_preset(item.text())
                self.presetsList.takeItem(self.presetsList.currentRow())
            except OSError as e:
                delete_preset_error(e, item.text())

    def __add_preset(self):
        dialog = NewPresetDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            preset_name = dialog.get_name()
            cue_type = dialog.get_type()

            exists = preset_exists(preset_name)
            if not (exists and not check_override_dialog(preset_name)):
                try:
                    write_preset(preset_name, {"_type_": cue_type})
                    if not exists:
                        self.presetsList.addItem(preset_name)
                except OSError as e:
                    write_preset_error(e, preset_name)

    def __rename_preset(self):
        item = self.presetsList.currentItem()
        if item is not None:
            new_name = save_preset_dialog(base_name=item.text())
            if new_name is not None and new_name != item.text():
                if preset_exists(new_name):
                    QMessageBox.warning(
                        self,
                        translate("Presets", "Warning"),
                        translate("Presets", "The same name is already used!"),
                    )
                else:
                    try:
                        rename_preset(item.text(), new_name)
                        item.setText(new_name)
                    except OSError as e:
                        rename_preset_error(e, item.text())

    def __edit_preset(self):
        item = self.presetsList.currentItem()
        if item is not None:
            try:
                preset = load_preset(item.text())
                if preset is not None:
                    try:
                        cue_class = CueFactory.create_cue(preset.get("_type_"))
                        cue_class = cue_class.__class__
                    except Exception:
                        cue_class = Cue

                    edit_dialog = CueSettingsDialog(cue_class)
                    edit_dialog.loadSettings(preset)
                    if edit_dialog.exec() == edit_dialog.Accepted:
                        preset.update(edit_dialog.getSettings())
                        try:
                            write_preset(item.text(), preset)
                        except OSError as e:
                            write_preset_error(e, item.text())
            except OSError as e:
                load_preset_error(e, item.text())

    def __cue_from_preset(self, preset_name):
        try:
            preset = load_preset(preset_name)
            if preset is not None:
                if CueFactory.has_factory(preset.get("_type_")):
                    cue = CueFactory.create_cue(preset["_type_"])

                    cue.update_properties(preset)
                    self.app.cue_model.add(cue)
                else:
                    QMessageBox.warning(
                        self,
                        translate("Presets", "Warning"),
                        translate(
                            "Presets",
                            "Cannot create a cue from this " "preset: {}",
                        ).format(preset_name),
                    )
        except OSError as e:
            load_preset_error(e, preset_name)

    def __cue_from_selected(self):
        for item in self.presetsList.selectedItems():
            self.__cue_from_preset(item.text())

    def __load_on_selected(self):
        item = self.presetsList.currentItem()
        if item is not None:
            preset_name = item.text()
            try:
                cues = self.app.layout.get_selected_cues()
                if cues:
                    load_on_cues(preset_name, cues)
            except OSError as e:
                load_preset_error(e, preset_name)

    def __export_presets(self):
        names = [item.text() for item in self.presetsList.selectedItems()]
        archive, _ = QFileDialog.getSaveFileName(
            self, directory="archive.presets", filter="*.presets"
        )

        if archive != "":
            if not archive.endswith(".presets"):
                archive += ".presets"
            try:
                export_presets(names, archive)
            except (OSError, BadZipFile):
                logger.exception(
                    translate("Presets", "Cannot export correctly.")
                )

    def __import_presets(self):
        archive, _ = QFileDialog.getOpenFileName(self, filter="*.presets")
        if archive != "":
            try:
                if import_has_conflicts(archive):
                    answer = QMessageBox.question(
                        self,
                        translate("Presets", "Presets"),
                        translate(
                            "Presets",
                            "Some presets already exists, " "overwrite?",
                        ),
                        buttons=QMessageBox.Yes | QMessageBox.Cancel,
                    )

                    if answer != QMessageBox.Yes:
                        return

                import_presets(archive)
                self.__populate()
            except (OSError, BadZipFile):
                logger.exception(
                    translate("Presets", "Cannot import correctly.")
                )

    def __selection_changed(self):
        selection = len(self.presetsList.selectedIndexes())

        self.editPresetButton.setEnabled(selection == 1)
        self.renamePresetButton.setEnabled(selection == 1)
        self.loadOnSelectedButton.setEnabled(selection == 1)
        self.removePresetButton.setEnabled(selection > 0)
        self.cueFromSelectedButton.setEnabled(selection > 0)
        self.exportSelectedButton.setEnabled(selection > 0)


class NewPresetDialog(QDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resize(320, 105)
        self.setMaximumSize(self.size())
        self.setMinimumSize(self.size())
        self.setModal(True)
        self.setLayout(QGridLayout())

        self.nameLabel = QLabel(self)
        self.layout().addWidget(self.nameLabel, 0, 0)

        self.nameLineEdit = QLineEdit(self)
        self.layout().addWidget(self.nameLineEdit, 0, 1)

        self.typeLabel = QLabel(self)
        self.layout().addWidget(self.typeLabel, 1, 0)

        self.typeComboBox = QComboBox(self)
        for cue_class in CueSettingsRegistry().ref_classes():
            self.typeComboBox.addItem(
                translate("CueName", cue_class.Name), cue_class.__name__
            )
        self.layout().addWidget(self.typeComboBox, 1, 1)

        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setStandardButtons(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.dialogButtons.accepted.connect(self.accept)
        self.dialogButtons.rejected.connect(self.reject)
        self.layout().addWidget(self.dialogButtons, 2, 0, 1, 2)

        self.layout().setColumnStretch(0, 1)
        self.layout().setColumnStretch(1, 3)

        self.retranslateUi()

    def retranslateUi(self):
        self.nameLabel.setText(translate("Presets", "Preset name"))
        self.typeLabel.setText(translate("Presets", "Cue type"))

    def get_name(self):
        return self.nameLineEdit.text()

    def get_type(self):
        return self.typeComboBox.currentData()
