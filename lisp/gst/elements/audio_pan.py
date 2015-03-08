##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################


from lisp.gst.gst_element import GstMediaElement
from lisp.repository import Gst


class AudioPan(GstMediaElement):

    Type = GstMediaElement.TYPE_PLUGIN
    Name = "AudioPan"

    def __init__(self, pipe):
        super().__init__()

        self._properties = {"panorama": .0}

        self._panorama = Gst.ElementFactory.make("audiopanorama", None)
        pipe.add(self._panorama)

        self._convert = Gst.ElementFactory.make("audioconvert", None)
        pipe.add(self._convert)

        self._panorama.link(self._convert)

    def properties(self):
        return self._properties

    def set_property(self, name, value):
        if name in self._properties:
            if name == "panorama":
                self._panorama.set_property("panorama", value)

    def sink(self):
        return self._panorama

    def src(self):
        return self._convert
