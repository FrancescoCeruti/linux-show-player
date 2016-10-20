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
from lisp.utils import elogging

__MODULES = {}


def load_modules():
    for name, module in load_classes(__package__, os.path.dirname(__file__)):
        try:
            __MODULES[name] = module()
            elogging.debug('MODULES: Loaded "{0}"'.format(name))
        except Exception as e:
            elogging.exception('Failed "{0}" lading'.format(name), e)


def translations(locale):
    base_path = os.path.dirname(__file__)
    for module in next(os.walk(base_path))[1]:
        tr_file = os.path.join(base_path, module)
        tr_file = os.path.join(tr_file, 'i18n')
        tr_file = os.path.join(tr_file, module + '_' + locale)

        yield tr_file


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
