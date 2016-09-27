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

import json
import os

from PyQt5.QtWidgets import QAction, QMenu
from lisp.cues.cue_factory import CueFactory

from lisp.application import Application

from lisp.core.module import Module
from lisp.layouts.cue_layout import CueLayout
from lisp.modules.presets.presets_ui import select_preset_dialog
from lisp.ui.mainwindow import MainWindow
from lisp.ui.ui_utils import translate
from lisp.utils import configuration
from lisp.utils import elogging


class Presets(Module):

    PRESETS_DIR = os.path.join(configuration.CFG_DIR, 'presets')

    def __init__(self):
        super().__init__()

        if not os.path.exists(Presets.PRESETS_DIR):
            os.makedirs(Presets.PRESETS_DIR, exist_ok=True)

        # Entry in mainWindow menu
        self.menu = QMenu(translate('Presets', 'Presets'))
        self.menu_action = MainWindow().menuTools.addMenu(self.menu)

        self.editPresetsAction = QAction(MainWindow())
        self.editPresetsAction.triggered.connect(self.__edit_presets)
        self.editPresetsAction.setText(
            translate('Presets', 'Edit presets'))

        self.cueFromPresetAction = QAction(MainWindow())
        self.cueFromPresetAction.triggered.connect(self.__cue_from_preset)
        self.cueFromPresetAction.setText(translate('Preset', 'Cue from preset'))

        self.loadOnSelectedAction = QAction(MainWindow())
        self.loadOnSelectedAction.triggered.connect(self.__load_on_selected)
        self.loadOnSelectedAction.setText(
            translate('Presets', 'Load preset on selected cues'))

        self.menu.addActions((
            self.editPresetsAction,
            self.cueFromPresetAction,
            self.loadOnSelectedAction
        ))

        self.loadOnCueAction = QAction(None)
        self.loadOnCueAction.triggered.connect(self.__load_on_cue)
        self.loadOnCueAction.setText(translate('Preset', 'Load preset'))

        self.createFromCueAction = QAction(None)
        self.createFromCueAction.triggered.connect(self.__create_from_cue)
        self.createFromCueAction.setText(translate('Preset', 'Save as preset'))

        CueLayout.cm_registry.add_separator()
        CueLayout.cm_registry.add_item(self.loadOnCueAction)
        CueLayout.cm_registry.add_item(self.createFromCueAction)
        CueLayout.cm_registry.add_separator()

    def __edit_presets(self):
        pass

    def __cue_from_preset(self):
        preset_name = select_preset_dialog(tuple(self.list_presets()))
        if preset_name is not None:
            preset = self.load_preset(preset_name)
            cue = CueFactory.create_cue(preset['_type_'])

            cue.update_properties(preset)
            Application().cue_model.add(cue)

    def __load_on_selected(self):
        preset_name = select_preset_dialog(tuple(self.list_presets()))
        if preset_name is not None:
            for cue in Application().layout.get_selected_cues():
                self.load_on_cue(preset_name, cue)

    def __load_on_cue(self):
        preset_name = select_preset_dialog(tuple(self.list_presets()))
        if preset_name is not None:
            self.load_on_cue(preset_name,
                             Application().layout.get_context_cue())

    def __create_from_cue(self):
        preset = Application().layout.get_context_cue().properties(
            only_changed=True)
        # Discard id and index
        preset.pop('id')
        preset.pop('index')

        self.write_preset('TEST', preset)

    def load_on_cue(self, preset_name, cue):
        cue.update_properties(self.load_preset(preset_name))

    @staticmethod
    def list_presets():
        try:
            for entry in os.scandir(Presets.PRESETS_DIR):
                if entry.is_file():
                    yield entry.name
        except OSError as e:
            elogging.exception(
                translate('Presets', 'Error while reading presets'), e)

    @staticmethod
    def load_preset(name):
        path = os.path.join(Presets.PRESETS_DIR, name)
        if os.path.exists(path):
            with open(path, mode='r') as in_file:
                return json.load(in_file)

        return {}

    @staticmethod
    def write_preset(name, preset):
        path = os.path.join(Presets.PRESETS_DIR, name)
        with open(path, mode='w') as out_file:
            json.dump(preset, out_file)
