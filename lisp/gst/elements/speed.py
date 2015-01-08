##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst

from lisp.gst.gst_element import GstMediaElement


class Speed(GstMediaElement):

    Type = GstMediaElement.TYPE_PLUGIN
    Name = "Speed"

    def __init__(self, pipe):
        super().__init__()

        self._properties = {"speed": 1.0}

        self._scaletempo = Gst.ElementFactory.make("scaletempo", None)
        pipe.add(self._scaletempo)

        self._convert = Gst.ElementFactory.make("audioconvert", None)
        pipe.add(self._convert)

        self._scaletempo.link(self._convert)

        self.__bus = pipe.get_bus()
        self.__bus.add_signal_watch()
        self.__handler = self.__bus.connect("message", self.__on_message)

        self._state = None

    def properties(self):
        return self._properties

    def set_property(self, name, value):
        if(name == "speed" and value != self._properties["speed"]):
            self._properties["speed"] = value

            if(self._state == Gst.State.PLAYING):
                self.__changeSpeed()

    def sink(self):
        return self._scaletempo

    def src(self):
        return self._convert

    def dispose(self):
        self.__bus.remove_signal_watch()
        self.__bus.disconnect(self.__handler)

    def __on_message(self, bus, message):
        if(message.type == Gst.MessageType.STATE_CHANGED and
                message.src == self._scaletempo):
            self._state = message.parse_state_changed()[1]
            if(self._state == Gst.State.PLAYING):
                self.__changeSpeed()

    def __changeSpeed(self):
        current_position = self._scaletempo.query_position(Gst.Format.TIME)[1]

        self._scaletempo.seek(self._properties['speed'],
                              Gst.Format.TIME,
                              Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE,
                              Gst.SeekType.SET,
                              current_position,
                              Gst.SeekType.NONE,
                              0)
