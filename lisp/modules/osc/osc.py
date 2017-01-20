# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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


from lisp.core.module import Module
from lisp.core.configuration import config
from lisp.ui.settings.app_settings import AppSettings
from lisp.modules.osc.osc_settings import OscSettings
from lisp.modules.osc.osc_common import OscCommon


class Osc(Module):
    """Provide OSC I/O functionality"""

    def __init__(self):
        # Register the settings widget
        AppSettings.register_settings_widget(OscSettings)

        if config['OSC'].getboolean('enabled') is True:
            OscCommon().start()
