# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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
import os
import re

from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class ModulesLoader:
    def __init__(self, pkg, pkg_path, exclude=()):
        """
        :param pkg: dotted name of the package
        :param pkg_path: path of the package to scan
        :param exclude: iterable of excluded modules names
        """
        self.pkg = pkg
        self.excluded = exclude
        self.pkg_path = pkg_path

    def __iter__(self):
        return self.load_modules()

    def load_modules(self):
        """Generate lists of tuples (class-name, class-object)."""
        for entry in os.scandir(self.pkg_path):

            # Exclude __init__, __pycache__ and likely
            if re.match("^__.*", entry.name):
                continue

            mod_name = entry.name
            if entry.is_file():
                # Split filename and extension
                mod_name, ext = os.path.splitext(entry.name)

                # Exclude all non-python files
                if not re.match(".py[cod]?", ext):
                    continue

            # Exclude excluded ¯\_(°^°)_/¯
            if mod_name in self.excluded:
                continue

            mod_path = self.pkg + "." + mod_name

            try:
                # Import module
                yield mod_name, import_module(mod_path)
            except Exception:
                logger.warning(
                    translate(
                        "ModulesLoaderWarning",
                        'Cannot load python module: "{0}"',
                    ).format(mod_name),
                    exc_info=True,
                )


class ClassLoader:
    """Generator for iterating over classes in a package.

    The class name must be the same as the module name, optionally
    suffixes and prefixes lists can be provided.

    Using a package __init__ module is possible to create sub-packages

    .. highlight::

        package
        |
        ├── module1.py
        |   |
        |   └──Module1
        |
        ├──── module_extra.py
        |     |
        |     └── ModuleExtra
        |
        └──── sub_package
              |
              └── __init__.py
                  |
                  └──SubPackage

    """

    def __init__(self, pkg, pkg_path, pre=("",), suf=("",), exclude=()):
        """
        :param pkg: dotted name of the package
        :param pkg_path: path of the package to scan
        :param pre: iterable of prefixes
        :param suf: iterable suffixes
        :param exclude: iterable of excluded modules names

        `pre` and `suf` must have the same length to work correctly, if some of
        the classes to load have no prefix/suffix an empty one should be used.
        """
        self.prefixes = pre
        self.suffixes = suf

        self._mods_loader = ModulesLoader(pkg, pkg_path, exclude)

    def __iter__(self):
        return self.load_classes()

    def load_classes(self):
        for mod_name, module in self._mods_loader:
            # Load classes from imported module
            for prefix, suffix in zip(self.prefixes, self.suffixes):
                cls_name = "undefined"
                try:
                    cls_name = module_to_class_name(mod_name, prefix, suffix)
                    if hasattr(module, cls_name):
                        cls = getattr(module, cls_name)
                        yield cls_name, cls
                except Exception:
                    logger.warning(
                        translate(
                            "ClassLoaderWarning",
                            'Cannot load python class: "{0}"',
                        ).format(cls_name),
                        exc_info=True,
                    )


def load_classes(pkg, pkg_path, pre=("",), suf=("",), exclude=()):
    return ClassLoader(pkg, pkg_path, pre, suf, exclude)


def module_to_class_name(mod_name, pre="", suf=""):
    """Return the supposed class name from loaded module.

    Substitutions:
     * Remove `underscores`
     * First letters to uppercase version

    For example:
     * For "module", the result will be "Module"
     * For "module_name", the result will be "ModuleName"
    """

    # Capitalize the first letter of each word
    base_name = "".join(word.title() for word in mod_name.split("_"))
    # Add prefix and suffix to the base name
    return pre + base_name + suf


def import_module(module_path):
    return __import__(module_path, globals(), locals(), ["*"])
