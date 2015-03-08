##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from lisp.gst.gst_element import GstMediaElement
from lisp.repository import Gst


class JackSink(GstMediaElement):

    Type = GstMediaElement.TYPE_OUTPUT
    Name = 'JackSink'

    CONNECT_NONE = 'none'
    CONNECT_AUTO = 'auto'
    CONNECT_AUTO_FORCED = 'auto-forced'

    def __init__(self, pipe):
        super().__init__()

        self._properies = {'server': None,
                           'client-name': 'Linux Show Player',
                           'connect': self.CONNECT_AUTO,
                           'volume': 1,
                           'mute': False}

        self._volume = Gst.ElementFactory.make('volume', None)
        pipe.add(self._volume)

        self._resample = Gst.ElementFactory.make('audioresample')
        pipe.add(self._resample)

        self._sink = Gst.ElementFactory.make('jackaudiosink', 'sink')
        self._sink.set_property('client-name', 'Linux Show Player')
        pipe.add(self._sink)

        self._volume.link(self._resample)
        self._resample.link(self._sink)

    def sink(self):
        return self._volume

    def properties(self):
        return self._properies

    def set_property(self, name, value):
        if name in self._properies:
            self._properies[name] = value
            if name in ['volume', 'mute']:
                self._volume.set_property(name, value)
            else:
                self._sink.set_property(name, value)
