# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2017 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2012-2016 Thomas Achtner <info@offtools.de>
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


from lisp.core.plugin import Plugin
from lisp.plugins.osc.osc_server import OscServer
from lisp.plugins.osc.osc_settings import OscSettings
from lisp.ui.settings.app_configuration import AppConfigurationDialog


# TODO: layout-controls in external plugin (now disabled, see osc_server.py)
class Osc(Plugin):
    """Provide OSC I/O functionality"""

    Name = 'OSC'
    Authors = ('Thomas Achtner', )
    Description = 'Provide OSC I/O functionality'

    def __init__(self, app):
        super().__init__(app)

        # Register the settings widget
        AppConfigurationDialog.registerSettingsWidget(
            'plugins.osc', OscSettings, Osc.Config)

        # Create a server instance
        self.__server = OscServer(
            Osc.Config['hostname'],
            Osc.Config['inPort'],
            Osc.Config['outPort']
        )

    @property
    def server(self):
        return self.__server

    def terminate(self):
        self.__server.stop()
