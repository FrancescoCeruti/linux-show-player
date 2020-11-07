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

import inspect
import itertools
import logging
import sys
from os import path
from typing import Dict, Type

from lisp import USER_PLUGINS_PATH, app_dirs, PLUGINS_PACKAGE, PLUGINS_PATH
from lisp.core.configuration import JSONFileConfiguration, DummyConfiguration
from lisp.core.loading import load_classes
from lisp.core.plugin import Plugin, PluginNotLoadedError
from lisp.core.plugin_loader import PluginsLoader
from lisp.ui.ui_utils import translate, install_translation

logger = logging.getLogger(__name__)


class PluginsManager:
    # Fallback plugin configuration
    FALLBACK_CONFIG = {"_version_": "undefined", "_enabled_": True}

    def __init__(self, application, enable_user_plugins=True):
        self.application = application
        self.enable_user_plugins = enable_user_plugins

        # The discovered plugins
        self.register: Dict[str, Type[Plugin]] = {}
        # Loaded plugins instances
        self.plugins: Dict[str, Plugin] = {}

    def load_plugins(self):
        """Load and instantiate available plugins."""

        # Plugins shipped in the package
        lisp_plugins = load_classes(PLUGINS_PACKAGE, PLUGINS_PATH)

        # Plugins installed by the user
        if self.enable_user_plugins:
            # Allow importing of python modules from the user plugins path.
            if USER_PLUGINS_PATH not in sys.path:
                sys.path.insert(1, USER_PLUGINS_PATH)

            user_plugins = load_classes("", USER_PLUGINS_PATH)
        else:
            user_plugins = ()

        # Register the plugins
        for name, plugin in itertools.chain(lisp_plugins, user_plugins):
            self.register_plugin(name, plugin)

        # Load (instantiate) the plugins
        # Note that PluginsLoader.load() is a generator, it will yield
        # each plugin when ready, so "self.plugins" will be update gradually,
        # allowing plugins to request other plugins in theirs __init__ method.
        self.plugins.update(
            PluginsLoader(self.application, self.register).load()
        )

    def register_plugin(self, name, plugin):
        if name in self.register:
            # Prevent user plugins to override those provided with lisp,
            # if the latter are register before.
            # More generically, if two plugins with same name are provided,
            # only the first will be kept.
            logger.error(
                translate(
                    "PluginsError",
                    'A plugin by the name of "{}" already exists.',
                ).format(name)
            )
            return

        try:
            mod_path = path.dirname(inspect.getfile(plugin))
            mod_name = plugin.__module__.split(".")[-1]

            # Load plugin configuration
            user_config_path = path.join(
                app_dirs.user_config_dir, mod_name + ".json"
            )
            default_config_path = path.join(mod_path, "default.json")
            if path.exists(default_config_path):
                # Configuration for file
                plugin.Config = JSONFileConfiguration(
                    user_config_path, default_config_path
                )
            else:
                # Fallback configuration, if the plugin didn't provide one
                plugin.Config = DummyConfiguration(self.FALLBACK_CONFIG.copy())

            # Load plugin translations
            install_translation(mod_name, tr_path=path.join(mod_path, "i18n"))

            # Register plugin
            self.register[name] = plugin
        except Exception:
            logger.exception(
                translate(
                    "PluginsError", 'Failed to register plugin: "{}"'
                ).format(name)
            )

    def is_loaded(self, plugin_name):
        return plugin_name in self.plugins

    def get_plugin(self, plugin_name):
        if self.is_loaded(plugin_name):
            return self.plugins[plugin_name]
        else:
            raise PluginNotLoadedError(
                translate(
                    "PluginsError", "The requested plugin is not loaded: {}"
                ).format(plugin_name)
            )

    def finalize_plugins(self):
        """Finalize all the plugins."""
        for name, plugin in self.plugins.items():
            try:
                plugin.finalize()
                logger.info(
                    translate("PluginsInfo", 'Plugin terminated: "{}"').format(
                        name
                    )
                )
            except Exception:
                logger.exception(
                    translate(
                        "PluginsError", 'Failed to terminate plugin: "{}"'
                    ).format(name)
                )

        self.plugins.clear()
