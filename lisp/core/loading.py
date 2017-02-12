# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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
import os.path
import re
import traceback

try:
    from os import scandir
except ImportError:
    from scandir import scandir


class load_classes:
    """Generator for iterating over classes in a package.

    The class name must be the same as the module name, optionally
    suffixes and prefixes lists can be provided.

    .. highlight::

        modules
        ├── module1.py
        |   └──Module1
        └── module_extra.py
            └── ModuleExtra

    """

    def __init__(self, pkg, pkg_path, pre=('',), suf=('',), exclude=()):
        """
        :param pkg: dotted name of the package
        :param pkg_path: path of the package to scan
        :param pre: iterable of prefixes
        :param suf: iterable suffixes
        :param exclude: iterable of excluded modules names

        `pre` and `suf` must have the same length to work correctly, if some of
        the classes to load have no prefix/suffix an empty one should be used.
        """
        self.pkg = pkg
        self.prefixes = pre
        self.suffixes = suf
        self.excluded = exclude
        self.pkg_path = pkg_path

    def __iter__(self):
        return self.load()

    def load(self):
        """Generate lists of tuples (class-name, class-object)."""
        for entry in scandir(self.pkg_path):

            # Exclude __init__, __pycache__ and likely
            if re.match('^__.*', entry.name):
                continue

            mod_name = entry.name
            if entry.is_file():
                # Split filename and extension
                mod_name, ext = os.path.splitext(entry.name)

                # Exclude all non-python files
                if not re.match('.py[cod]?', ext):
                    continue

            # Exclude excluded ¯\_(ツ)_/¯
            if mod_name in self.excluded:
                continue

            mod_path = self.pkg + '.' + mod_name

            try:
                # Import module
                module = import_module(mod_path)

                # Load class from imported module
                for prefix, suffix in zip(self.prefixes, self.suffixes):
                    name = self._class_name(mod_name, prefix, suffix)
                    if hasattr(module, name):
                        cls = getattr(module, name)
                        yield (name, cls)

            except ImportError:
                logging.warning('Cannot load module: {0}'.format(mod_name))
                logging.debug(traceback.format_exc())

    @staticmethod
    def _class_name(mod_name, pre='', suf=''):
        """Return the supposed class name from loaded module.

        Substitutions:
         * Remove `underscores`
         * First letters to uppercase version

        For example:
         * For "module", the result will be "Module"
         * For "module_name", the result will be "ModuleName"
        """

        # Capitalize the first letter of each word
        base_name = ''.join(word.title() for word in mod_name.split('_'))
        # Add prefix and suffix to the base name
        return pre + base_name + suf


def import_module(module_path):
    return __import__(module_path, globals(), locals(), ['*'])
