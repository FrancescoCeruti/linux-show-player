##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import gi
gi.require_version('Gst', '1.0')

from lisp.gst.gst_element import GstMediaElement
from gi.repository import Gst


class AutoSink(GstMediaElement):

    Type = GstMediaElement.TYPE_OUTPUT
    Name = 'AutoSink'

    def __init__(self, pipe):
        super().__init__()

        self._properies = {'volume': 1,
                           'mute': False}

        self._volume = Gst.ElementFactory.make('volume', None)
        pipe.add(self._volume)

        self._sink = Gst.ElementFactory.make('autoaudiosink', 'sink')
        pipe.add(self._sink)

        self._volume.link(self._sink)

    def sink(self):
        return self._volume

    def set_property(self, name, value):
        if name in self._properies:
            self._properies[name] = value
            self._volume.set_property(name, value)
