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

from importlib import import_module
from os.path import dirname
import traceback

from lisp.utils import logging
from lisp.utils.dyamic_loader import class_name_from_module
from lisp.utils.util import find_packages


__PLUGINS = {}


def init_plugins():
    for pkg in find_packages(path=dirname(__file__)):
        try:
            class_name = class_name_from_module(pkg)
            module = import_module('lisp.plugins.' + pkg + '.' + pkg)

            __PLUGINS[pkg] = getattr(module, class_name)()
            logging.debug('PLUGINS: Loaded "' + pkg + '"')
        except Exception:
            logging.error('PLUGINS: Failed "' + pkg + '" load')
            logging.debug('PLUGINS: ' + traceback.format_exc())


def reset_plugins():
    """ Resets and removes all the plugins """
    for plugin in __PLUGINS:
        try:
            __PLUGINS[plugin].reset()
            logging.debug('PLUGINS: Reset "' + plugin + '"')
        except Exception:
            logging.error('PLUGINS: Failed "' + plugin + '" reset')
            logging.debug('PLUGINS: ' + traceback.format_exc())

    __PLUGINS.clear()


def set_plugins_settings(settings):
    failed = []

    for plugin in __PLUGINS.values():
        if plugin.Name in settings:
            try:
                plugin.load_settings(settings[plugin.Name])
            except Exception as e:
                logging.error('PLUGINS: Failed "' + plugin.Name + '" '
                              'settings load')
                logging.debug('PLUGINS: ' + traceback.format_exc())
                failed.append((plugin.Name, e))

    return failed


def get_plugin_settings():
    settings = {}

    for plugin in __PLUGINS.values():
        try:
            p_settings = plugin.settings()
            if p_settings is not None and len(p_settings) > 0:
                settings[plugin.Name] = p_settings
        except Exception:
            logging.error('PLUGINS: Failed "' + plugin.Name + '" '
                          'settings retrieve')
            logging.debug('PLUGINS: ' + traceback.format_exc())

    return settings
