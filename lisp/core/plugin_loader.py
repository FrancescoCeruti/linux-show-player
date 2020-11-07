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
from typing import Dict, Type, Iterable

from lisp.core.plugin import Plugin, logger
from lisp.ui.ui_utils import translate


class PluginLoadException(Exception):
    pass


class PluginInitFailedException(PluginLoadException):
    pass


class PluginsLoader:
    def __init__(
        self,
        application,
        to_load: Dict[str, Type[Plugin]],
    ):
        self.application = application
        self.to_load = to_load

        self.resolved = set()
        self.unresolved = set()
        self.failed = set()

    def load(self):
        yield from self._resolve_dependencies(
            self.to_load.keys(), optionals=True, log_level=logging.ERROR
        )

    def _resolve_plugin_dependencies(self, plugin: Type[Plugin]):
        self.unresolved.add(plugin)

        try:
            yield from self._resolve_dependencies(plugin.Depends)
            yield from self._resolve_dependencies(
                plugin.OptDepends, optionals=True
            )

            self.resolved.add(plugin)
        except PluginLoadException as e:
            raise PluginLoadException(
                translate(
                    "PluginsError", "Cannot satisfy dependencies for plugin: {}"
                ).format(plugin.Name),
            ) from e
        finally:
            self.unresolved.remove(plugin)

    def _resolve_dependencies(
        self,
        dependencies: Iterable[str],
        optionals: bool = False,
        log_level: int = logging.WARNING,
    ):
        for dependency_name in dependencies:
            try:
                dependency = self._dependency_from_name(dependency_name)
                if self._should_resolve(dependency):
                    yield from self._resolve_plugin_dependencies(dependency)
                    yield from self._load_plugin(dependency, dependency_name)
            except PluginLoadException as e:
                logger.log(log_level, str(e), exc_info=e)
                if not optionals:
                    raise e

    def _load_plugin(self, plugin: Type[Plugin], name: str):
        # Try to load the plugin, if enabled
        if plugin.Config.get("_enabled_", False):
            try:
                # Create an instance of the plugin and yield it
                yield name, plugin(self.application)
                logger.info(
                    translate("PluginsInfo", "Plugin loaded: {}").format(
                        plugin.Name
                    )
                )
            except Exception as e:
                self.failed.add(plugin)
                raise PluginInitFailedException(
                    f"Failed to initialize plugin: {plugin.Name}"
                ) from e
        else:
            raise PluginLoadException("Plugin disabled, not loaded.")

    def _should_resolve(self, plugin: Type[Plugin]) -> bool:
        if plugin in self.failed:
            raise PluginLoadException(
                f"Plugin is in error state: {plugin.Name}"
            )

        if plugin not in self.resolved:
            if plugin in self.unresolved:
                raise PluginLoadException("Circular dependency detected.")

            return True

        return False

    def _dependency_from_name(self, name: str) -> Type[Plugin]:
        try:
            return self.to_load[name]
        except KeyError:
            raise PluginLoadException(f"No plugin named '{name}'")
