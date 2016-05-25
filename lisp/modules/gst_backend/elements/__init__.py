import os

from lisp.backend.media_element import ElementType
from lisp.utils.dyamic_loader import ClassesLoader


__INPUTS = {}
__OUTPUTS = {}
__PLUGINS = {}


def load():
    for _, element in ClassesLoader(os.path.dirname(__file__)):
        if element.ElementType == ElementType.Input:
            __INPUTS[element.Name] = element
        elif element.ElementType == ElementType.Output:
            __OUTPUTS[element.Name] = element
        elif element.ElementType == ElementType.Plugin:
            __PLUGINS[element.Name] = element


# Getter functions
def inputs():
    return __INPUTS


def outputs():
    return __OUTPUTS


def plugins():
    return __PLUGINS
