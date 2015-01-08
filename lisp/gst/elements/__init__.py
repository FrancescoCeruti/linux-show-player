import os

from lisp.core.media_element import MediaElement
from lisp.utils.dyamic_loader import load_classes


__INPUTS = {}
__OUTPUTS = {}
__PLUGINS = {}


def load():
    for _, element in load_classes(os.path.dirname(__file__)):
        if element.Type == MediaElement.TYPE_INPUT:
            __INPUTS[element.Name] = element
        elif element.Type == MediaElement.TYPE_OUTPUT:
            __OUTPUTS[element.Name] = element
        elif element.Type == MediaElement.TYPE_PLUGIN:
            __PLUGINS[element.Name] = element


# Getter functions
def inputs():
    return __INPUTS


def outputs():
    return __OUTPUTS


def plugins():
    return __PLUGINS
