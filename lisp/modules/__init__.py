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

__MODULES = {}


def load_modules():
    for name, module in load_classes(__package__, os.path.dirname(__file__)):
        try:
            __MODULES[name] = module()
            elogging.debug('MODULES: Loaded "{0}"'.format(name))
        except Exception as e:
            elogging.exception('Failed "{0}" lading'.format(name), e)


def translations():
    base_path = os.path.dirname(os.path.realpath(__file__))
    for module in next(os.walk(base_path))[1]:
        i18n_dir = os.path.join(base_path, module, 'i18n')
        if os.path.exists(i18n_dir):
            yield os.path.join(i18n_dir, module)


def terminate_modules():
    for module_name in __MODULES:
        try:
            __MODULES[module_name].terminate()
            elogging.debug('MODULES: Terminated "{0}"'.format(module_name))
        except Exception as e:
            elogging.exception('Failed "{0}" termination'.format(module_name),
                               e)


def check_module(modname):
    return modname.lower() in [mod.lower() for mod in __MODULES]
