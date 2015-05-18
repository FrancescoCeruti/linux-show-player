# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
#
# Linux Show Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linux Show Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>.

from lisp.backends.base.media_element import ElementType, MediaType
from lisp.backends.gst.gst_element import GstMediaElement
from lisp.backends.gst.gi_repository import Gst


class UserElement(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Audio
    Name = "Personalized"

    _properties_ = ('bin', )

    def __init__(self, pipe):
        super().__init__()

        self._pipe = pipe

        self._sink = Gst.ElementFactory.make("audioconvert", None)
        # A default assignment for the bin
        self._bin = Gst.ElementFactory.make("identity", None)
        self._bin.set_property("signal-handoffs", False)
        self._src = Gst.ElementFactory.make("audioconvert", None)

        pipe.add(self._sink)
        pipe.add(self._bin)
        pipe.add(self._src)

        self._sink.link(self._bin)
        self._bin.link(self._src)

        self.__bin = ''

        # Connect the pipeline bus for getting state-changes
        self.__bus = pipe.get_bus()
        self.__bus.add_signal_watch()
        self.__handler = self.__bus.connect("message", self.__on_message)

        self._state = None

    @property
    def bin(self):
        return self.__bin

    @bin.setter
    def bin(self, value):
        if value != "" and value != self.__bin:
            self.__bin = value

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
            if playing:
                self._pipe.set_state(Gst.State.PLAYING)

    def sink(self):
        return self._sink

    def src(self):
        return self._src

    def dispose(self):
        self.__bus.remove_signal_watch()
        self.__bus.disconnect(self.__handler)

    def __on_message(self, bus, message):
        if (message.type == Gst.MessageType.STATE_CHANGED and
                    message.src == self._bin):
            self._state = message.parse_state_changed()[1]
