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

import os

from PyQt5.QtWidgets import QAction

from lisp.core.plugin import Plugin
from lisp.layout.cue_layout import CueLayout
from lisp.layout.cue_menu import (
    MenuActionsGroup,
    SimpleMenuAction,
    MENU_PRIORITY_PLUGIN,
)
from lisp.plugins.presets.lib import (
    PRESETS_DIR,
    load_on_cue,
    preset_exists,
    load_on_cues,
)
from lisp.plugins.presets.presets_ui import (
    select_preset_dialog,
    PresetsDialog,
    save_preset_dialog,
    check_override_dialog,
    write_preset,
    load_preset_error,
    write_preset_error,
)
from lisp.ui.ui_utils import translate


class Presets(Plugin):

    Name = "Preset"
    Authors = ("Francesco Ceruti",)
    Description = "Allow to save, edit, import and export cue presets"

    def __init__(self, app):
        super().__init__(app)

        if not os.path.exists(PRESETS_DIR):
            os.makedirs(PRESETS_DIR, exist_ok=True)

        # Entry in mainWindow menu
        self.manageAction = QAction(self.app.window)
        self.manageAction.triggered.connect(self.__edit_presets)
        self.manageAction.setText(translate("Presets", "Presets"))

        self.app.window.menuTools.addAction(self.manageAction)

        # Cue menu (context-action)
        self.cueActionsGroup = MenuActionsGroup(
            submenu=True,
            text=translate("Presets", "Presets"),
            priority=MENU_PRIORITY_PLUGIN,
        )
        self.cueActionsGroup.add(
            SimpleMenuAction(
                translate("Presets", "Load on cue"),
                self.__load_on_cue,
                translate("Presets", "Load on selected cues"),
                self.__load_on_cues,
            ),
            SimpleMenuAction(
                translate("Presets", "Save as preset"), self.__create_from_cue
            ),
        )

        CueLayout.CuesMenu.add(self.cueActionsGroup)

    def __edit_presets(self):
        ui = PresetsDialog(self.app, parent=self.app.window)
        ui.show()

    def __load_on_cue(self, cue):
        preset_name = select_preset_dialog()
        if preset_name is not None:
            try:
                load_on_cue(preset_name, cue)
            except OSError as e:
                load_preset_error(e, preset_name)

    def __load_on_cues(self, cues):
        preset_name = select_preset_dialog()
        if preset_name is not None:
            try:
                load_on_cues(preset_name, cues)
            except OSError as e:
                load_preset_error(e, preset_name)

    def __create_from_cue(self, cue):
        name = save_preset_dialog(cue.name)

        if name is not None:
            if not (preset_exists(name) and not check_override_dialog(name)):
                preset = cue.properties(defaults=False)

                # Discard id and index
                preset.pop("id")
                preset.pop("index")

                try:
                    write_preset(name, preset)
                except OSError as e:
                    write_preset_error(e, name)
