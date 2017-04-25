# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2016-2017 Aurélien Cibrario <aurelien.cibrario@gmail.com>
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

from lisp.application import Application
from lisp.core.configuration import config
from lisp.core.plugin import Plugin
from lisp.layouts.list_layout.layout import ListLayout
from lisp.modules.midi import midi_utils
from lisp.modules.midi.midi_input import MIDIInput
from lisp.plugins.list_layout_controller.list_layout_controller_settings import ListLayoutControllerSetting
from lisp.ui.mainwindow import MainWindow
from lisp.ui.settings.app_settings import AppSettings


class ListLayoutController(Plugin):

    Name = 'ListLayoutController'

    def __init__(self):
        super().__init__()

        self.__midi_mapping = {}

    def init(self):

        if isinstance(Application().layout, ListLayout):
            AppSettings.register_settings_widget(ListLayoutControllerSetting)

            self.__keyword_to_action = {
                'gomidimapping': Application().layout.goButton.click,
                'stopmidimapping': Application().layout.controlButtons.stopButton.click,
                'pausemidimapping': Application().layout.controlButtons.pauseButton.click,
                'fadeinmidimapping': Application().layout.controlButtons.fadeInButton.click,
                'fadeoutmidimapping': Application().layout.controlButtons.fadeOutButton.click,
                'resumemidimapping': Application().layout.controlButtons.resumeButton.click,
                'interruptmidimapping': Application().layout.controlButtons.interruptButton.click,
                'prevcuemidimapping' : Application().layout.set_current_index_prev,
                'nextcuemidimapping' : Application().layout.set_current_index_next
            }

            MIDIInput().new_message.connect(self.on_new_midi_message)
            MainWindow().app_settings_updated.connect(self.load_mapping_from_config)
            self.load_mapping_from_config()

    def load_mapping_from_config(self):
        self.__midi_mapping = {}

        for keyword, mapping in config['ListLayoutController'].items():
            self.__midi_mapping[keyword] = mapping

    def on_new_midi_message(self, message):
        msg_dict = midi_utils.str_msg_to_dict(str(message))
        try:
            msg_dict.pop('velocity')
        except KeyError:
            pass
        simplified_msg = midi_utils.dict_msg_to_str(msg_dict)

        for keyword, mapping in self.__midi_mapping.items():
            if mapping == simplified_msg:
                self.__keyword_to_action[keyword]()

