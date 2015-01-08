##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from importlib import import_module
import logging
from os.path import dirname
import traceback

from lisp.utils.dyamic_loader import class_name_from_module
from lisp.utils.util import find_packages


__PLUGINS = {}


def init_plugins():
    failed = []

    for pkg in find_packages(path=dirname(__file__)):
        try:
            class_name = class_name_from_module(pkg)
            module = import_module('lisp.plugins.' + pkg + '.' + pkg)

            __PLUGINS[pkg] = getattr(module, class_name)()
            logging.debug('PLUGINS: Loaded "' + pkg + '"')
        except Exception as e:
            logging.error('PLUGINS: Failed "' + pkg + '" load')
            logging.debug('PLUGINS: ' + traceback.format_exc())
            failed.append((pkg, e))

    return failed


def reset_plugins():
    ''' Resets and removes all the plugins '''
    for plugin in __PLUGINS:
        try:
            __PLUGINS[plugin].reset()
            logging.debug('PLUGINS: Reseted "' + plugin + '"')
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
    failed = []

    for plugin in __PLUGINS.values():
        try:
            settings = plugin.get_settings()
            if settings is not None:
                settings[plugin.Name] = settings
        except Exception as e:
            logging.error('PLUGINS: Failed "' + plugin.Name + '" '
                          'settings retrieve')
            logging.debug('PLUGINS: ' + traceback.format_exc())
            failed.append((plugin.Name, e))

    return failed
