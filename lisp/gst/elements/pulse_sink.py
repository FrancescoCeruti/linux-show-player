##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import gi
gi.require_version('Gst', '1.0')

from lisp.gst.gst_element import GstMediaElement
from gi.repository import Gst


class PulseSink(GstMediaElement):

    Type = GstMediaElement.TYPE_OUTPUT
    Name = 'PulseAudioSink'

    def __init__(self, pipe):
        super().__init__()

        self._properies = {'server': None,
                           'device': None,
                           'volume': 1,
                           'mute': False,
                           'client-name': 'Linux Show Player'
                           }

        self._sink = Gst.ElementFactory.make('pulsesink', 'sink')
        self._sink.set_property('client-name', 'Linux Show Player')
        pipe.add(self._sink)

    def sink(self):
        return self._sink

    def properties(self):
        return self._properies

    def set_property(self, name, value):
        if name in self._properies:
            self._properies[name] = value
            self._sink.set_property(name, value)
