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
    def is_disabled(cls):
        return not cls.Config.get("_enabled_", False)

    @classmethod
    def is_loaded(cls):
        return cls.State & PluginState.Loaded

    @classmethod
    def status_icon(cls):
        if cls.is_disabled():
            return 'led-off'
        if cls.State & PluginState.InError:
            return 'led-error'
        if cls.State & PluginState.InWarning:
            return 'led-pause'
        return 'led-running'
