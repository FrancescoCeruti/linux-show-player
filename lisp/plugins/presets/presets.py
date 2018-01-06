# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2017 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtWidgets import QAction

from lisp.core.plugin import Plugin
from lisp.layouts.cue_layout import CueLayout
from lisp.plugins.presets.lib import PRESETS_DIR, load_on_cue, preset_exists
from lisp.plugins.presets.presets_ui import select_preset_dialog, \
    PresetsDialog, save_preset_dialog, check_override_dialog, write_preset, \
    load_preset_error, write_preset_error
from lisp.ui.ui_utils import translate


class Presets(Plugin):

    Name = 'Preset'
    Authors = ('Francesco Ceruti', )
    Description = 'Allow to save, edit, import and export cue presets'

    def __init__(self, app):
        super().__init__(app)

        if not os.path.exists(PRESETS_DIR):
            os.makedirs(PRESETS_DIR, exist_ok=True)

        # Entry in mainWindow menu
        self.manageAction = QAction(self.app.window)
        self.manageAction.triggered.connect(self.__edit_presets)
        self.manageAction.setText(translate('Presets', 'Presets'))

        self.menu_action = self.app.window.menuTools.addAction(self.manageAction)

        self.loadOnCueAction = QAction(None)
        self.loadOnCueAction.triggered.connect(self.__load_on_cue)
        self.loadOnCueAction.setText(translate('Presets', 'Load preset'))

        self.createFromCueAction = QAction(None)
        self.createFromCueAction.triggered.connect(self.__create_from_cue)
        self.createFromCueAction.setText(translate('Presets', 'Save as preset'))

        CueLayout.cm_registry.add_separator()
        CueLayout.cm_registry.add_item(self.loadOnCueAction)
        CueLayout.cm_registry.add_item(self.createFromCueAction)
        CueLayout.cm_registry.add_separator()

    def __edit_presets(self):
        ui = PresetsDialog(self.app, parent=self.app.window)
        ui.show()

    def __load_on_cue(self):
        preset_name = select_preset_dialog()
        if preset_name is not None:
            try:
                load_on_cue(preset_name, self.app.layout.get_context_cue())
            except OSError as e:
                load_preset_error(e, preset_name, parent=self.app.window)

    def __create_from_cue(self):
        cue = self.app.layout.get_context_cue()
        name = save_preset_dialog(cue.name)

        if name is not None:
            if not (preset_exists(name) and not check_override_dialog(name)):
                preset = cue.properties(only_changed=True)

                # Discard id and index
                preset.pop('id')
                preset.pop('index')

                try:
                    write_preset(name, preset)
                except OSError as e:
                    write_preset_error(e, name, parent=self.app.window)
