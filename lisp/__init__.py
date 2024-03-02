# This file is part of Linux Show Player
#
# Copyright 2017 Francesco Ceruti <ceppofrancy@gmail.com>
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

import os
from os import path

from appdirs import AppDirs

__author__ = "Francesco Ceruti"
__email__ = "ceppofrancy@gmail.com"
__url__ = "https://github.com/FrancescoCeruti/linux-show-player"
__license__ = "GPLv3"
__version_info__ = (0, 6, 1)
__version__ = ".".join(map(str, __version_info__))

# The version passed follows <major>.<minor>
app_dirs = AppDirs(
    "LinuxShowPlayer", version="{}.{}".format(*__version_info__[0:2])
)

# Application wide "constants"
APP_DIR = path.dirname(__file__)
I18N_DIR = path.join(APP_DIR, "i18n", "qm")

DEFAULT_APP_CONFIG = path.join(APP_DIR, "default.json")
USER_APP_CONFIG = path.join(app_dirs.user_config_dir, "lisp.json")

PLUGINS_PACKAGE = "lisp.plugins"
PLUGINS_PATH = path.join(APP_DIR, "plugins")
USER_PLUGINS_PATH = path.join(app_dirs.user_data_dir, "plugins")

DEFAULT_CACHE_DIR = path.join(app_dirs.user_data_dir, "cache")

ICON_THEMES_DIR = path.join(APP_DIR, "ui", "icons")
ICON_THEME_COMMON = "lisp"

RUNNING_IN_FLATPAK = "FLATPAK_ID" in os.environ
