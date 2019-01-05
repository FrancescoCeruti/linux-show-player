# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from lisp.core.loading import load_classes

__PROTOCOLS = {}


def load_protocols():
    for name, protocol_class in load_classes(__package__, dirname(__file__)):
        __PROTOCOLS[protocol_class.Name] = protocol_class


def get_protocol(name):
    """
    :param name: protocol name
    :type name: str
    :rtype: type[TimecodeProtocol]
    """
    return __PROTOCOLS[name]


def list_protocols():
    """
    :return: list of protocol names
    :rtype: list
    """
    return list(__PROTOCOLS.keys())
