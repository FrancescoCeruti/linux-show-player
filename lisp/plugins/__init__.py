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
import logging
from os import path

from lisp import app_dirs
from lisp.core.configuration import JSONFileConfiguration
from lisp.core.loading import load_classes
from lisp.ui.ui_utils import install_translation, translate

PLUGINS = {}

FALLBACK_CONFIG_PATH = path.join(path.dirname(__file__), "default.json")

logger = logging.getLogger(__name__)


class PluginNotLoadedError(Exception):
    pass


class PluginState:
    Listed = 0
    Loaded = 1

    DependenciesNotSatisfied = 4
    OptionalDependenciesNotSatisfied = 8

    InError = DependenciesNotSatisfied
    InWarning = OptionalDependenciesNotSatisfied


def load_plugins(application):
    """Load and instantiate available plugins."""
    for name, plugin in load_classes(__package__, path.dirname(__file__)):
        try:
            PLUGINS[name] = plugin

            mod_path = path.dirname(inspect.getfile(plugin))
            mod_name = plugin.__module__.split(".")[-1]

            if path.exists(path.join(mod_path, "default.json")):
                default_config_path = path.join(mod_path, "default.json")
            else:
                default_config_path = FALLBACK_CONFIG_PATH

            # Load plugin configuration
            config = JSONFileConfiguration(
                path.join(app_dirs.user_config_dir, mod_name + ".json"),
                default_config_path,
            )
            plugin.Config = config

            # Load plugin (self-contained) translations
            install_translation(mod_name, tr_path=path.join(mod_path, "i18n"))
        except Exception:
            logger.exception(
                translate("PluginsError", 'Failed to load "{}"').format(name)
            )

    __init_plugins(application)


def __init_plugins(application):
    pending = PLUGINS.copy()

    # Run until all the pending plugins are loaded (unless interrupted)
    while pending:
        # Load all plugins with satisfied dependencies
        unresolved = not __load_plugins(pending, application)

        # If no plugin with satisfied dependencies is found try again
        # ignoring optional-dependencies
        if unresolved:
            unresolved = not __load_plugins(pending, application, False)

        if unresolved:
            # We've go through all the not loaded plugins and weren't able
            # to resolve their dependencies, which means there are cyclic or
            # missing/disabled dependencies
            logger.warning(
                translate(
                    "PluginsWarning", "Cannot satisfy dependencies for: {}"
                ).format(", ".join(pending))
            )

            return


def __load_plugins(plugins, application, optionals=True):
    """
    Go through each plugin and check if it's dependencies are already loaded,
    otherwise leave it in the pending dict.
    If all of it's dependencies are satisfied then try to load it.

    :type typing.MutableMapping[str, Type[lisp.core.plugin.Plugin]]
    :type application: lisp.application.Application
    :type optionals: bool
    :rtype: bool
    """
    resolved = False

    for name, plugin in list(plugins.items()):
        dependencies = plugin.Depends
        if optionals:
            dependencies += plugin.OptDepends

        for dep in dependencies:
            if dep not in PLUGINS or not PLUGINS[dep].is_loaded():
                if dep in plugin.Depends:
                    plugin.State |= PluginState.DependenciesNotSatisfied
                else:
                    plugin.State |= PluginState.OptionalDependenciesNotSatisfied
                break
        else:
            plugins.pop(name)
            resolved = True
            plugin.State &= ~(PluginState.DependenciesNotSatisfied | PluginState.OptionalDependenciesNotSatisfied)

            for dep in plugin.OptDepends:
                if dep not in PLUGINS or not PLUGINS[dep].is_loaded():
                    plugin.State |= PluginState.OptionalDependenciesNotSatisfied
                    break

            # Try to load the plugin, if enabled
            try:
                if plugin.is_enabled():
                    # Create an instance of the plugin and save it
                    PLUGINS[name] = plugin(application)
                    logger.info(
                        translate("PluginsInfo", 'Plugin loaded: "{}"').format(
                            name
                        )
                    )
                else:
                    logger.debug(
                        translate(
                            "PluginsDebug",
                            'Plugin disabled in configuration: "{}"',
                        ).format(name)
                    )
            except Exception:
                logger.exception(
                    translate(
                        "PluginsError",
                        'Failed to load plugin: "{}"'.format(name),
                    )
                )
    return resolved


def finalize_plugins():
    """Finalize all the plugins."""
    for plugin_name, plugin in PLUGINS.items():
        if not plugin.is_loaded():
            continue
        try:
            PLUGINS[plugin_name].finalize()
            logger.info(
                translate("PluginsInfo", 'Plugin terminated: "{}"').format(
                    plugin_name
                )
            )
        except Exception:
            logger.exception(
                translate(
                    "PluginsError", 'Failed to terminate plugin: "{}"'
                ).format(plugin_name)
            )


def is_loaded(plugin_name):
    return plugin_name in PLUGINS and PLUGINS[plugin_name].is_loaded()


def get_plugin(plugin_name):
    if is_loaded(plugin_name):
        return PLUGINS[plugin_name]
    else:
        raise PluginNotLoadedError(
            translate(
                "PluginsError", "the requested plugin is not loaded: {}"
            ).format(plugin_name)
        )
