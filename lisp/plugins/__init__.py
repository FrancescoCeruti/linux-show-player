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

from lisp.core.loading import load_classes
from lisp.ui import elogging

__PLUGINS = {}


def load_plugins():
    """Load available plugins."""
    for name, plugin in load_classes(__package__, os.path.dirname(__file__)):
        try:
            __PLUGINS[name] = plugin()
            elogging.debug('PLUGINS: Loaded "{0}"'.format(name))
        except Exception as e:
            elogging.exception('PLUGINS: Failed "{0}" load'.format(name), e)


def translations():
    base_path = os.path.dirname(os.path.realpath(__file__))
    for module in next(os.walk(base_path))[1]:
        i18n_dir = os.path.join(base_path, module, 'i18n')
        if os.path.exists(i18n_dir):
            yield os.path.join(i18n_dir, module)


def init_plugins():
    """Initialize all the plugins."""
    failed = []
    for plugin in __PLUGINS:
        try:
            __PLUGINS[plugin].init()
            elogging.debug('PLUGINS: Initialized "{0}"'.format(plugin))
        except Exception as e:
            failed.append(plugin)
            elogging.exception('PLUGINS: Failed "{0}" init'.format(plugin), e)

    for plugin in failed:
        __PLUGINS.pop(plugin)


def reset_plugins():
    """Resets all the plugins."""
    for plugin in __PLUGINS:
        try:
            __PLUGINS[plugin].reset()
            elogging.debug('PLUGINS: Reset "{0}"'.format(plugin))
        except Exception as e:
            elogging.exception('PLUGINS: Failed "{0}" reset'.format(plugin), e)


def set_plugins_settings(settings):
    for plugin in __PLUGINS.values():
        if plugin.Name in settings:
            try:
                plugin.load_settings(settings[plugin.Name])
            except Exception as e:
                elogging.exception('PLUGINS: Failed "{0}" settings load'
                                   .format(plugin.Name), e)


def get_plugin_settings():
    plugins_settings = {}

    for plugin in __PLUGINS.values():
        try:
            settings = plugin.settings()
            if settings is not None and len(settings) > 0:
                plugins_settings[plugin.Name] = settings
        except Exception as e:
            elogging.exception('PLUGINS: Failed "{0}" settings retrieve'
                               .format(plugin.Name), e)

    return plugins_settings
