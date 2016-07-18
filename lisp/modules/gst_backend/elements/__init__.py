import os

from lisp.backend.media_element import ElementType
from lisp.utils.dyamic_loader import ClassesLoader


__INPUTS = {}
__OUTPUTS = {}
__PLUGINS = {}


def load():
    for _, element_class in ClassesLoader(os.path.dirname(__file__)):
        if element_class.ElementType == ElementType.Input:
            __INPUTS[element_class.__name__] = element_class
        elif element_class.ElementType == ElementType.Output:
            __OUTPUTS[element_class.__name__] = element_class
        elif element_class.ElementType == ElementType.Plugin:
            __PLUGINS[element_class.__name__] = element_class


# Getter functions
def inputs():
    return __INPUTS


def input_name(class_name):
    return __INPUTS[class_name].Name


def outputs():
    return __OUTPUTS


def output_name(class_name):
    return __OUTPUTS[class_name].Name


def plugins():
    return __PLUGINS


def plugin_name(class_name):
    return __PLUGINS[class_name].Name