##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from lisp.gst.gst_element import GstMediaElement
from lisp.repository import Gst


MIN_dB = 0.000000312  # -100dB


class Audiodynamic(GstMediaElement):

    Type = GstMediaElement.TYPE_PLUGIN
    Name = "AudioDynamic"

    def __init__(self, pipe):
        super().__init__()

        self._properties = {"mode": "compressor",
                            "characteristics": "hard-knee",
                            "ratio": 1,
                            "threshold": 1
                            }

        self._dynamic = Gst.ElementFactory.make("audiodynamic", None)
        pipe.add(self._dynamic)

        self._converter = Gst.ElementFactory.make("audioconvert", None)
        pipe.add(self._converter)

        self._dynamic.link(self._converter)

    def properties(self):
        return self._properties

    def set_property(self, name, value):
        if(name in self._properties):
            self._properties[name] = value
            self._dynamic.set_property(name, value)

    def sink(self):
        return self._dynamic

    def src(self):
        return self._converter
