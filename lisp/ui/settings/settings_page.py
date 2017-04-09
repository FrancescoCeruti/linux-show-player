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

from PyQt5.QtWidgets import QWidget


class SettingsPage(QWidget):
    Name = 'Page'
    MinHeight = 350
    MinWidth = 400

    def enable_check(self, enabled):
        """Enable option check"""

    def get_settings(self):
        """Return the current settings."""
        return {}

    def load_settings(self, settings):
        """Load the settings."""


class CueSettingsPage(SettingsPage):
    Name = 'Cue page'

    def __init__(self, cue_class, **kwargs):
        super().__init__(**kwargs)

        self._cue_class = cue_class
