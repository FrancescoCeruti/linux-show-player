##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from lisp.gst.gst_element import GstMediaElement
from lisp.repository import Gst


class Volume(GstMediaElement):

    Type = GstMediaElement.TYPE_PLUGIN
    Name = "Volume"

    def __init__(self, pipe):
        super().__init__()

        self._properties = {"volume": 1.0,
                            "mute": False,
                            "normal_volume": 1.0
                            }

        self._volume = Gst.ElementFactory.make("volume", None)
        pipe.add(self._volume)

        self._normal = Gst.ElementFactory.make("volume", None)
        pipe.add(self._normal)

        self._convert = Gst.ElementFactory.make("audioconvert", None)
        pipe.add(self._convert)

        self._volume.link(self._normal)
        self._normal.link(self._convert)

    def properties(self):
        return self._properties

    def set_property(self, name, value):
        if name in self._properties:
            self._properties[name] = value
            if name == "volume" or name == "mute":
                self._volume.set_property(name, value)
            elif name == "normal_volume":
                self._normal.set_property("volume", value)

    def sink(self):
        return self._volume

    def src(self):
        return self._convert
