##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst

from PyQt5.QtCore import QObject, pyqtSignal

from lisp.gst.gst_element import GstMediaElement


class Dbmeter(QObject, GstMediaElement):

    Type = GstMediaElement.TYPE_PLUGIN
    Name = "DbMeter"

    levelReady = pyqtSignal(list, list, list)

    def __init__(self, pipe):
        super().__init__()

        self._properties = {"interval": 50 * Gst.MSECOND,
                            "peak-ttl": Gst.SECOND,
                            "peak-falloff": 20
                            }

        self._level = Gst.ElementFactory.make("level", None)
        self._level.set_property('post-messages', True)
        pipe.add(self._level)

        self._convert = Gst.ElementFactory.make("audioconvert", None)
        pipe.add(self._convert)

        self._level.link(self._convert)

        self.__bus = pipe.get_bus()
        self.__bus.add_signal_watch()
        self.__handler = self.__bus.connect("message::element",
                                            self.__on_message)

        self.update_properties(self._properties)

    def dispose(self):
        self.__bus.remove_signal_watch()
        self.__bus.disconnect(self.__handler)

    def properties(self):
        return self._properties

    def set_property(self, name, value):
        if name in self._properties:
            self._properties[name] = value
            self._level.set_property(name, value)

    def sink(self):
        return self._level

    def src(self):
        return self._convert

    def __on_message(self, bus, msg):
        if msg.src == self._level:
            struct = msg.get_structure()
            if struct is not None and struct.has_name('level'):
                self.levelReady.emit(struct.get_value('peak'),
                                     struct.get_value('rms'),
                                     struct.get_value('decay'))
