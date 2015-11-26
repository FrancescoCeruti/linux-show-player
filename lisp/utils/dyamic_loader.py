# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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
import pkgutil
import traceback


class ClassesLoader:
    """Generator for iterating over classes in a package.

    The class name must be the same as the module name, optionally
    suffixes and prefixes lists can be provided.

    .. Example:

        elements_package
        |__element1.py
        |  |__Element1
        |__element_extra.py
           |__ElementExtra
    """

    def __init__(self, package_path, prefixes=None, suffixes=None,
                 excluded=None):
        """
        :param package_path: location of the classes (package)
        :type package_path: str
        :param prefixes: list of prefixes (symmetrical with suffixes)
        :type prefixes: list
        :param suffixes: list of suffixes (symmetrical with prefixes)
        :type suffixes: list
        """
        self._package_path = package_path
        self._prefixes = prefixes if prefixes is not None else ['']
        self._suffixes = suffixes if suffixes is not None else ['']
        self._excluded = excluded if excluded is not None else []

    def __iter__(self):
        return self.load()

    def load(self):
        """ Generate lists of tuples (class-name, class-object) """
        modules = pkgutil.iter_modules(path=(self._package_path, ))

        for loader, mod_name, _ in modules:
            if mod_name in self._excluded:
                continue

            # Import module
            module = loader.find_module(mod_name).load_module()

            # Load class from imported module
            partial = []
            for prefix, suffix in zip(self._prefixes, self._suffixes):
                try:
                    name = class_name_from_module(mod_name, prefix, suffix)
                    cls = getattr(module, name)
                    partial.append((name, cls))
                except Exception:
                    logging.warning(
                        'Failed loading module: ' + mod_name)
                    logging.debug(traceback.format_exc())

            # Yield the class name and the class-object
            if len(partial) == 1:
                yield partial[0]
            elif partial:
                yield partial


def class_name_from_module(mod_name, pre='', suf=''):
    """Return the class name for a dynamic loaded module

    If the name is like "module_name", the result will be "ModuleName"

    :param mod_name: the module name
    :param pre: prefix for the class name (default '')
    :param suf: suffix for the class name (default '')
    """

    # Capitalize the first letter of each word
    base_name = ''.join(word.title() for word in mod_name.split('_'))
    # Add prefix and suffix to the base name
    return pre + base_name + suf
