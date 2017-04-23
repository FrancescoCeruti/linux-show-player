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


class ListLayoutController(Plugin):

    Name = 'ListLayoutController'

    def init(self):

        ListLayoutSettings.register_extra_settings(ListLayoutControllerSetting)

        # FIXME : this will crash if option is not in config file.
        # TODO : find the way to deal with new application option
        self.__go_midi_mapping = config['ListLayout']['gomidimapping']
        print(self.__go_midi_mapping)

        MIDIInput().new_message.connect(self.do_something_when_midi_triggered)

    def do_something_when_midi_triggered(self, message):
        print(f'I do something with {message} !')
        print(type(message))
