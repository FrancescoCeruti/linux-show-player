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

import logging

from lisp.core.configuration import DummyConfiguration
from lisp.ui.ui_utils import translate
from lisp import __version__ as lisp_version

logger = logging.getLogger(__name__)


class PluginNotLoadedError(Exception):
    pass


class PluginState:
    Listed = 0
    Loaded = 1

    DependenciesNotSatisfied = 2
    OptionalDependenciesNotSatisfied = 4

    Error = DependenciesNotSatisfied
    Warning = OptionalDependenciesNotSatisfied


class Plugin:
    """Base class for plugins."""

    Name = "Plugin"
    CorePlugin = False
    Depends = ()
    OptDepends = ()
    Authors = ("None",)
    Description = "No Description"
    Version = lisp_version

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
    def is_enabled(cls) -> bool:
        """Returns True if the plugin is configured as 'enabled'."""
        return cls.CorePlugin or cls.Config.get("_enabled_", False)

    @classmethod
    def set_enabled(cls, enabled: bool):
        """Enable or disable the plugin.
        Does not load the plugin, only updates its configuration.
        """
        if not cls.CorePlugin:
            cls.Config.set("_enabled_", enabled)
            cls.Config.write()

    @classmethod
    def is_loaded(cls):
        """Returns True if the plugin has been loaded."""
        return bool(cls.State & PluginState.Loaded)

    @classmethod
    def status_text(cls):
        if cls.State & PluginState.Error:
            return translate(
                "PluginsStatusText",
                "An error has occurred with this plugin. "
                "Please see logs for further information.",
            )

        if cls.State & PluginState.Warning:
            if cls.is_enabled():
                return translate(
                    "PluginsStatusText",
                    "A non-critical issue is affecting this plugin. "
                    "Please see logs for further information.",
                )

            return translate(
                "PluginsStatusText",
                "There is a non-critical issue with this disabled plugin. "
                "Please see logs for further information.",
            )

        if cls.is_enabled():
            return translate(
                "PluginsStatusText", "Plugin loaded and ready for use."
            )

        return translate("PluginsStatusText", "Plugin disabled. Enable to use.")
