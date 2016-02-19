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

from lisp.core.module import Module
from lisp.modules.midi.input_handler import MIDIInputHandler
from lisp.modules.midi.midi_settings import MIDISettings
from lisp.modules.midi.output_provider import MIDIOutputProvider
from lisp.ui.settings.app_settings import AppSettings
from lisp.utils.configuration import config


class Midi(Module):
    """Provide MIDI I/O functionality"""

    def __init__(self):
        # Register the settings widget
        AppSettings.register_settings_widget(MIDISettings)

        port_name = config['MIDI']['InputDevice']
        backend_name = config['MIDI']['Backend']

        MIDIInputHandler(port_name=port_name, backend_name=backend_name)
        MIDIInputHandler().start()

        try:
            MIDIOutputProvider(port_name=port_name, backend_name=backend_name)
            MIDIOutputProvider().start()
        except Exception as e:
            MIDIInputHandler().stop()
            raise e

    def terminate(self):
        # Stop the MIDI-event Handler
        MIDIInputHandler().stop()
        MIDIOutputProvider().stop()
