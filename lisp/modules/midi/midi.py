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

import mido

from lisp.core.configuration import config
from lisp.core.module import Module
from lisp.modules.midi.midi_settings import MIDISettings
from lisp.ui.settings.app_settings import AppSettings


class Midi(Module):
    """Provide MIDI I/O functionality"""

    def __init__(self):
        # Register the settings widget
        AppSettings.register_settings_widget(MIDISettings)

        bk_name = config['MIDI']['Backend']
        try:
            # Load the backend and set as current mido backend
            mido.set_backend(mido.Backend(bk_name, load=True))
        except Exception:
            raise RuntimeError('Backend loading failed: {0}'.format(bk_name))
