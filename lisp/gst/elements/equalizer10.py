##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from lisp.gst.gst_element import GstMediaElement
from lisp.repository import Gst


class Equalizer10(GstMediaElement):

    Type = GstMediaElement.TYPE_PLUGIN
    Name = "Equalizer-10bands"

    def __init__(self, pipe):
        super().__init__()

        self._properties = {"band0": 0, "band1": 0, "band2": 0, "band3": 0,
                            "band4": 0, "band5": 0, "band6": 0, "band7": 0,
                            "band8": 0, "band9": 0
                            }

        self._equalizer = Gst.ElementFactory.make("equalizer-10bands", None)
        pipe.add(self._equalizer)

        self._converter = Gst.ElementFactory.make("audioconvert", None)
        pipe.add(self._converter)

        self._equalizer.link(self._converter)

    def properties(self):
        return self._properties

    def set_property(self, name, value):
        if name in self._properties:
            self._properties[name] = value
            self._equalizer.set_property(name, value)

    def sink(self):
        return self._equalizer

    def src(self):
        return self._converter
