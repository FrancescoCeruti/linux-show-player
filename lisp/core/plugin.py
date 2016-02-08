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


class Plugin:
    """Interface for plugins.

    The "init" and "reset" functions are called respectively after the session
    layout is created (init) and before (reset).
    """

    Name = 'Plugin'

    def init(self):
        """Initialize the session-related components of the plugin."""

    def reset(self):
        """Reset the session-related components of plugin."""

    def settings(self):
        """Return the plugin settings.

        :rtype: dict
        """
        return {}

    def load_settings(self, settings):
        """Load the plugin settings.

        :param settings: the settings to be loaded
        :type settings: dict
        """
