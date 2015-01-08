##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from importlib import import_module
import logging
from os.path import dirname
import traceback

from lisp.utils.util import find_packages


__MODULES = {}


def init_modules():
    failed = []

    for pkg in find_packages(path=dirname(__file__)):
        try:
            mod = import_module('lisp.modules.' + pkg)
            mod.initialize()
            __MODULES[pkg] = mod
            logging.debug('MODULES: Loaded "' + pkg + '"')
        except Exception as e:
            logging.error('MODULES: Failed "' + pkg + '" loading')
            logging.debug('MODULES: ' + traceback.format_exc())
            failed.append((pkg, e))

    return failed


def terminate_modules():
    for mod in __MODULES:
        try:
            __MODULES[mod].terminate()
            logging.debug('MODULES: Module "' + mod + '" terminated')
        except Exception:
            logging.error('MODULES: Module "' + mod + '" termination failed')
            logging.debug('MODULES: ' + traceback.format_exc())


def check_module(modname):
    return modname in __MODULES
