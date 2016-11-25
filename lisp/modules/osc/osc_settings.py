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


from PyQt5.QtCore import QTime, QT_TRANSLATE_NOOP


from lisp.ui.settings.settings_page import SettingsPage


class OscSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'OSC settings')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_settings(self):
        conf = {
            'inport': 9001,
            'outport': 9002,
            'hostname': 'localhost',
            'feedback': True
        }

        return {'OSC': conf}

    def load_settings(self, settings):
        pass