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

from os.path import dirname
import traceback

from lisp.utils import logging
from lisp.utils.dyamic_loader import load_classes


__MODULES = {}


def init_modules():
    for module_name, module in load_classes(dirname(__file__)):
        try:
            __MODULES[module_name] = module()
            logging.debug('MODULES: Loaded "{0}'.format(module_name))
        except Exception as e:
            logging.error('Failed "{0}" loading'.format(module_name),
                          details=str(e))
            logging.debug(traceback.format_exc())


def terminate_modules():
    for module_name in __MODULES:
        try:
            __MODULES[module_name].terminate()
            logging.debug(
                'MODULES: Module "{0}" terminated'.format(module_name))
        except Exception as e:
            logging.error(
                'MODULES: Module "{0}" termination failed'.format(module_name),
                details=str(e))
            logging.debug(traceback.format_exc())


def check_module(modname):
    return modname in __MODULES
