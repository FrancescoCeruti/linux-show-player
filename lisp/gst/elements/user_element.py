##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from lisp.gst.gst_element import GstMediaElement
from lisp.repository import Gst


class UserElement(GstMediaElement):

    Type = GstMediaElement.TYPE_PLUGIN
    Name = "Personalized"

    def __init__(self, pipe):
        super().__init__()

        self._properties = {"bin": ""}
        self._pipe = pipe

        self._sink = Gst.ElementFactory.make("audioconvert", None)
        pipe.add(self._sink)

        # A default assignment for the bin
        self._bin = Gst.ElementFactory.make("identity", None)
        self._bin.set_property("signal-handoffs", False)
        pipe.add(self._bin)

        self._src = Gst.ElementFactory.make("audioconvert", None)
        pipe.add(self._src)

        self._sink.link(self._bin)
        self._bin.link(self._src)

        # Connect the pipeline bus for getting state-changes
        self.__bus = pipe.get_bus()
        self.__bus.add_signal_watch()
        self.__handler = self.__bus.connect("message", self.__on_message)

        self._state = None

    def properties(self):
        return self._properties

    def set_property(self, name, value):
        if(name == "bin" and value != "" and value != self._properties["bin"]):
            self._properties["bin"] = value

            # If in playing we need to restart the pipeline after unblocking
            playing = self._state == Gst.State.PLAYING
            # Block the stream
            pad = self._sink.sinkpads[0]
            probe = pad.add_probe(Gst.PadProbeType.BLOCK, lambda *a: 0, "")

            # Unlink the components
            self._sink.unlink(self._bin)
            self._bin.unlink(self._src)
            self._pipe.remove(self._bin)

            # Create the bin, when fail use a do-nothing element
            try:
                self._bin = Gst.parse_bin_from_description(value, True)
            except Exception:
                self._bin = Gst.ElementFactory.make("identity", None)
                self._bin.set_property("signal-handoffs", False)

            # Link the components
            self._pipe.add(self._bin)
            self._sink.link(self._bin)
            self._bin.link(self._src)

            # Unblock the stream
            pad.remove_probe(probe)
            if(playing):
                self._pipe.set_state(Gst.State.PLAYING)

    def sink(self):
        return self._sink

    def src(self):
        return self._src

    def dispose(self):
        self.__bus.remove_signal_watch()
        self.__bus.disconnect(self.__handler)

    def __on_message(self, bus, message):
        if(message.type == Gst.MessageType.STATE_CHANGED and
                message.src == self._bin):
            self._state = message.parse_state_changed()[1]
