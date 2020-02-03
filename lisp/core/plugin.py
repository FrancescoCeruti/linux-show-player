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

from lisp.core.configuration import DummyConfiguration
from lisp.plugins import PluginState
from lisp.ui.ui_utils import translate


# TODO: add possible additional metadata (Icon, Version, ...)
class Plugin:
    """Base class for plugins."""

    Name = "Plugin"
    Depends = ()
    OptDepends = ()
    Authors = ("None",)
    Description = "No Description"
    Config = DummyConfiguration()
    State = PluginState.Listed

    def __init__(self, app):
        """:type app: lisp.application.Application"""
        self.__app = app
        self.__class__.State |= PluginState.Loaded

    @property
    def app(self):
        """:rtype: lisp.application.Application"""
        return self.__app

    def finalize(self):
        """Called when the application is getting closed."""
        self.__class__.State &= ~PluginState.Loaded

    @classmethod
    def is_enabled(cls):
        return cls.Config.get("_enabled_", False)

    @classmethod
    def is_loaded(cls):
        return cls.State & PluginState.Loaded

    @classmethod
    def status_icon(cls):
        if cls.State & PluginState.InError:
            return 'led-error'

        if cls.State & PluginState.InWarning:
            if cls.is_enabled():
                return 'led-pause'
            return 'led-pause-outline'

        if cls.is_enabled():
            return 'led-running'
        return 'led-off'

    @classmethod
    def status_tooltip(cls):
        if cls.State & PluginState.InError:
            return translate('PluginsTooltip', 'An error has occurred with this plugin. Please see logs for further information.')

        if cls.State & PluginState.InWarning:
            if cls.is_enabled():
                return translate('PluginsTooltip', 'A non-critical issue is affecting this plugin. Please see logs for further information.')
            return translate('PluginsTooltip', 'There is a non-critical issue with this disabled plugin. Please see logs for further information.')

        if cls.is_enabled():
            return translate('PluginsTooltip', 'Plugin loaded and ready for use.')
        return translate('PluginsTooltip', 'Plugin disabled. Enable to use.')
