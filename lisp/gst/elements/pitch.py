##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst

from lisp.gst.gst_element import GstMediaElement


class Pitch(GstMediaElement):

    Type = GstMediaElement.TYPE_PLUGIN
    Name = "Pitch"

    def __init__(self, pipe):
        super().__init__()

        self._properties = {"pitch": 0}

        self._pitch = Gst.ElementFactory.make("pitch", None)
        pipe.add(self._pitch)

        self._converter = Gst.ElementFactory.make("audioconvert", None)
        pipe.add(self._converter)

        self._pitch.link(self._converter)

    def properties(self):
        return self._properties

    def set_property(self, name, value):
        if(name in self._properties):
            self._properties[name] = value
            self._pitch.set_property(name, value)

    def sink(self):
        return self._pitch

    def src(self):
        return self._converter
