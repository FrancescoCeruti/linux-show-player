# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2017 Francesco Ceruti <ceppofrancy@gmail.com>
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

from os import path

__author__ = 'Francesco Ceruti'
__email__ = 'ceppofrancy@gmail.com'
__url__ = 'https://github.com/FrancescoCeruti/linux-show-player'
__license__ = 'GPLv3'
__version__ = '0.6dev'

# Application wide "constants"
APP_DIR = path.dirname(__file__)

USER_DIR = path.join(path.expanduser("~"), '.linux_show_player')

LOGS_DIR = path.join(USER_DIR, 'logs')

DEFAULT_APP_CONFIG = path.join(APP_DIR, 'default.json')
USER_APP_CONFIG = path.join(USER_DIR, 'lisp.json')

I18N_PATH = path.join(APP_DIR, 'i18n', 'qm')

ICON_THEMES_DIR = path.join(APP_DIR, 'ui', 'icons')
ICON_THEME_COMMON = 'lisp'
