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

import inspect
import logging
import os
from collections.abc import Collection
from importlib import import_module
from pathlib import Path

from packaging.version import parse as version_parse

from lisp.core.collections.nested_dict import NestedDict
from lisp.core.has_properties import Property, HasInstanceProperties
from lisp.core.signal import Signal
from lisp.core.util import typename, last_index

logger = logging.getLogger(__name__)


class Session(HasInstanceProperties):
    layout_type = Property(default="")
    layout = Property(default={})

    session_file = Property(default="")
    """The current session-file path, must be absolute."""

    def __init__(self, layout):
        super().__init__()
        self.finalized = Signal()

        self.layout_type = typename(layout)
        self.layout = layout

        self.cue_model = layout.cue_model

    def name(self):
        """Return the name of session, depending on the session-file."""
        if self.session_file:
            return os.path.splitext(os.path.basename(self.session_file))[0]
        else:
            return "Untitled"

    def dir(self):
        """Return the current session-file path."""
        if self.session_file:
            return os.path.dirname(self.session_file)
        else:
            return os.path.expanduser("~")

    def abs_path(self, rel_path):
        """Return an absolute version of the given path."""
        if not os.path.isabs(rel_path):
            return os.path.normpath(os.path.join(self.dir(), rel_path))

        return rel_path

    def rel_path(self, abs_path):
        """Return a relative (to the session-file) version of the given path."""
        return os.path.relpath(abs_path, start=self.dir())

    def finalize(self):
        self.layout.finalize()
        self.cue_model.reset()

        self.finalized.emit()


class SessionMigrator:
    def __init__(
        self, app_version: str, app_dir: str | Path, plugins: Collection
    ):
        self.app_version = app_version
        self.app_dir = Path(app_dir)
        self.plugins = plugins

    def migrate(self, session_path: str, session_dict: dict) -> bool:
        has_run_migrations = False
        session_dict = NestedDict(session_dict)
        session_app_version = session_dict.get("meta.version", None)
        session_plugins_versions = session_dict.get("meta.plugins", {})

        if session_app_version is None:
            if "session" in session_dict:
                # Handle 0.6 dev version
                session_app_version = "0.6.0"
                session_plugins_versions = {
                    name: "0.6.0" for name, _ in self.plugins
                }
            else:
                # Handle 0.5 version
                session_app_version = "0.5.0"
                session_plugins_versions = {
                    name: "0.5.0" for name, _ in self.plugins
                }

        if version_parse(self.app_version) > version_parse(session_app_version):
            logger.debug(
                f"Version mismatch for application: found {session_app_version} - current {self.app_version}"
            )
            has_run_migrations |= self.migrate_package(
                session_path,
                session_dict,
                "lisp.migrations",
                self.app_dir.joinpath("migrations"),
                session_app_version,
            )

        for name, plugin in self.plugins:
            session_plugin_version = session_plugins_versions.get(name, None)

            if session_plugin_version is None:
                continue

            if version_parse(plugin.Version) <= version_parse(
                session_plugin_version
            ):
                continue

            module = inspect.getmodule(plugin)
            plugin_dir = Path(inspect.getfile(module)).parent

            logger.debug(
                f"Version mismatch for plugin {name}: found {session_plugin_version} - current {plugin.Version}"
            )
            has_run_migrations |= self.migrate_package(
                session_path,
                session_dict,
                f"{module.__package__}.migrations",
                plugin_dir.joinpath("migrations"),
                session_plugin_version,
            )

        return has_run_migrations

    def migrate_package(
        self,
        session_path: str,
        session_dict: NestedDict,
        package: str,
        package_path: Path,
        package_version: str,
    ) -> bool:
        migrations = [
            path.stem
            for path in package_path.glob("*.py")
            if path.is_file() and path.stem != "__init__"
        ]

        if len(migrations) <= 0:
            return False

        # Add a "start" migration, and sort the list,
        # then we slice the list to find the migrations we need to apply
        start_migration = package_version.replace(".", "_")
        migrations.append(f"from_{start_migration}")
        migrations.sort(key=self.__migrations_sort_key)
        migrations = migrations[
            : last_index(migrations, f"from_{start_migration}")
        ]

        for name in migrations:
            module_path = f"{package}.{name}"
            module = import_module(module_path)

            if hasattr(module, "migrate"):
                logger.debug(f"Running session migration: {module_path}")
                module.migrate(session_path, session_dict)
            else:
                logger.warning(f"Invalid session migration: {module_path}")

        return len(migrations) > 0

    @staticmethod
    def __migrations_sort_key(version: str):
        return version_parse(version.replace("from_", "").replace("_", "."))
