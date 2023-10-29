# This file is part of Linux Show Player
#
# Copyright 2020 Francesco Ceruti <ceppofrancy@gmail.com>
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

from typing import Optional

from lisp.core.plugins_manager import PluginsManager

DefaultPluginsManager: Optional[PluginsManager] = None


def load_plugins(application, enable_user_plugins=True):
    global DefaultPluginsManager
    if DefaultPluginsManager is None:
        DefaultPluginsManager = PluginsManager(application, enable_user_plugins)

    DefaultPluginsManager.load_plugins()


def finalize_plugins():
    if DefaultPluginsManager is not None:
        DefaultPluginsManager.finalize_plugins()


def is_loaded(plugin_name):
    return (
        DefaultPluginsManager is not None
        and DefaultPluginsManager.is_loaded(plugin_name)
    )


def get_plugins():
    if DefaultPluginsManager is not None:
        return DefaultPluginsManager.get_plugins()
    else:
        raise RuntimeError("Cannot get plugins before they have been loaded.")


def get_plugin(plugin_name):
    if DefaultPluginsManager is not None:
        return DefaultPluginsManager.get_plugin(plugin_name)
    else:
        raise RuntimeError("Cannot get plugins before they have been loaded.")
