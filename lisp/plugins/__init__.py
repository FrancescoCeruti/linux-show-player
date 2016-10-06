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

import os
import traceback

from lisp.core.loading import load_classes
from lisp.utils import elogging

__PLUGINS = {}


def load_plugins():
    """Load available plugins."""
    for name, plugin in load_classes(__package__, os.path.dirname(__file__)):
        try:
            __PLUGINS[name] = plugin()
            elogging.debug('PLUGINS: Loaded "{0}"'.format(name))
        except Exception:
            elogging.error('PLUGINS: Failed "{0}" load'.format(name))
            elogging.debug('PLUGINS: {0}'.format(traceback.format_exc()))


def translations():
    base_path = os.path.abspath('lisp/plugins')
    for module in next(os.walk(base_path))[1]:
        tr_file = os.path.join(base_path, module)
        tr_file = os.path.join(tr_file, 'i18n')
        tr_file = os.path.join(tr_file, module)

        yield tr_file


def init_plugins():
    """Initialize all the plugins."""
    for plugin in __PLUGINS:
        try:
            __PLUGINS[plugin].init()
            elogging.debug('PLUGINS: Initialized "{0}"'.format(plugin))
        except Exception:
            __PLUGINS.pop(plugin)
            elogging.error('PLUGINS: Failed "{0}" init'.format(plugin))
            elogging.debug('PLUGINS: {0}'.format(traceback.format_exc()))


def reset_plugins():
    """Resets all the plugins."""
    for plugin in __PLUGINS:
        try:
            __PLUGINS[plugin].reset()
            elogging.debug('PLUGINS: Reset "{0}"'.format(plugin))
        except Exception:
            elogging.error('PLUGINS: Failed "{0}" reset'.format(plugin))
            elogging.debug('PLUGINS: {0}'.format(traceback.format_exc()))


def set_plugins_settings(settings):
    failed = []

    for plugin in __PLUGINS.values():
        if plugin.Name in settings:
            try:
                plugin.load_settings(settings[plugin.Name])
            except Exception as e:
                elogging.error('PLUGINS: Failed "{0}" settings load'
                               .format(plugin.Name))
                elogging.debug('PLUGINS: {0}'.format(traceback.format_exc()))
                failed.append((plugin.Name, e))

    return failed


def get_plugin_settings():
    plugins_settings = {}

    for plugin in __PLUGINS.values():
        try:
            settings = plugin.settings()
            if settings is not None and len(settings) > 0:
                plugins_settings[plugin.Name] = settings
        except Exception:
            elogging.error('PLUGINS: Failed "{0}" settings retrieve'
                           .format(plugin.Name))
            elogging.debug('PLUGINS: {0}'.format(traceback.format_exc()))

    return plugins_settings
