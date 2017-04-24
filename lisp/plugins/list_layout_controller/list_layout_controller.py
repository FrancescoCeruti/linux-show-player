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

from lisp.core.configuration import config
from lisp.core.plugin import Plugin
from lisp.layouts.list_layout.list_layout_settings import ListLayoutSettings
from lisp.modules.midi.midi_input import MIDIInput
from lisp.plugins.list_layout_controller.list_layout_controller_settings import ListLayoutControllerSetting
from lisp.modules.midi import midi_utils
from lisp.application import Application
from lisp.layouts.list_layout.layout import ListLayout



class ListLayoutController(Plugin):

    Name = 'ListLayoutController'

    def init(self):

        ListLayoutSettings.register_extra_settings(ListLayoutControllerSetting)

        self.__midi_mapping = {}
        self.__midi_mapping = self.load_mapping_from_config()

        if isinstance(Application().layout, ListLayout):
            MIDIInput().new_message.connect(self.do_something_when_midi_triggered)
            print('midi signal connected !')
        print('init of plugin done')

    def load_mapping_from_config(self):
        # FIXME : this will crash if option is not in config file.
        # TODO : find the right way to deal with new application option
        cfg = config['ListLayout']['gomidimapping']
        restored_message = midi_utils.str_msg_to_dict(cfg)

        return restored_message

    def do_something_when_midi_triggered(self, message):
        msg = midi_utils.str_msg_to_dict(str(message))

        if message.type != 'polytouch':
            print(f"msg from config : {self.__midi_mapping}")
            print(f"msg received : {msg}")

        if msg['channel'] == self.__midi_mapping['channel']:
            if msg['type'] == self.__midi_mapping['type']:
                if msg['note'] == self.__midi_mapping['note']:
                    Application().layout.go()
                    print('Trigger activated')

