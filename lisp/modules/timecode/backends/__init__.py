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

from os.path import dirname
from lisp.ui import elogging
from lisp.core.loading import load_classes

# TODO: proper error handling if OLA could not imported
try:
    import ola
except ImportError:
    ola = False

__BACKENDS = {}


def load():
    if not ola:
       exclude = 'artnet'
    else:
        exclude = ''

    try:
        for name, backend_class in load_classes(__package__, dirname(__file__), exclude=exclude):
            __BACKENDS[backend_class.Name] = backend_class
            elogging.debug('TIMECODE: Loaded Backend "{0}"'.format(name))
    except Exception as e:
        elogging.exception('TIMECODE: Failed Backend "{0}" loading'.format(name), e)


def get(name):
    if name in __BACKENDS and callable(__BACKENDS[name]):
        return __BACKENDS[name]()
    else:
        RuntimeError("Timecode Backend - {0} not found".format(name))


def list():
    return __BACKENDS