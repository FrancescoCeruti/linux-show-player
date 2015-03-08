##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from lisp.gst.gst_element import GstMediaElement
from lisp.repository import Gst


class UriInput(GstMediaElement):

    Type = GstMediaElement.TYPE_INPUT
    Name = "URIInput"

    def __init__(self, pipe):
        super().__init__()

        self._properties = {"uri": "",
                            "use-buffering": False,
                            "download": False,
                            "buffer-size": -1
                            }

        self._decoder = Gst.ElementFactory.make("uridecodebin", None)
        pipe.add(self._decoder)

        self._convert = Gst.ElementFactory.make("audioconvert", None)
        pipe.add(self._convert)

        self._handler = self._decoder.connect("pad-added", self.__on_pad_added)

    def input_uri(self):
        return self._properties["uri"]

    def properties(self):
        return self._properties

    def dispose(self):
        self._decoder.disconnect(self._handler)

    def set_property(self, name, value):
        if(name in self._properties and value != self._properties[name]):
            self._properties[name] = value
            self._decoder.set_property(name, value)

    def src(self):
        return self._convert

    def __on_pad_added(self, *args):
        self._decoder.link(self._convert)
