# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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

from lisp.backend.media_element import ElementType
from lisp.core.loading import load_classes

__INPUTS = {}
__OUTPUTS = {}
__PLUGINS = {}


def load():
    for _, element_class in load_classes(__package__, dirname(__file__)):
        if element_class.ElementType == ElementType.Input:
            __INPUTS[element_class.__name__] = element_class
        elif element_class.ElementType == ElementType.Output:
            __OUTPUTS[element_class.__name__] = element_class
        elif element_class.ElementType == ElementType.Plugin:
            __PLUGINS[element_class.__name__] = element_class


# Getter functions
def inputs():
    return __INPUTS.copy()


def input_name(class_name):
    return __INPUTS[class_name].Name


def outputs():
    return __OUTPUTS.copy()


def output_name(class_name):
    return __OUTPUTS[class_name].Name


def plugins():
    return __PLUGINS.copy()


def plugin_name(class_name):
    return __PLUGINS[class_name].Name

def element_name(class_name):
    return all_elements()[class_name].Name


def all_elements():
    elements = inputs()
    elements.update(plugins())
    elements.update(outputs())
    return elements
