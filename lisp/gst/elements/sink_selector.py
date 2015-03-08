##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from threading import Lock

from lisp.gst import elements

from lisp.gst.gst_element import GstMediaElement
from lisp.repository import Gst


class SinkSelector(GstMediaElement):

    Type = GstMediaElement.TYPE_OUTPUT
    Name = "SinkSelector"

    Sinks = elements.outputs()

    def __init__(self, pipe):
        super().__init__()

        self._pipe = pipe
        self._state = Gst.State.NULL
        self._tee = Gst.ElementFactory.make("tee", None)
        self._pipe.add(self._tee)

        self.__wait_for_playing = Lock()
        self.__to_remove = []
        self.__to_add = []
        self.__bins = {}
        self.__sinks = {}

        self.__bus = pipe.get_bus()
        self.__bus.add_signal_watch()
        self.__handler = self.__bus.connect("message::state-changed",
                                            self.__on_message)

        self.__build_sink("sink0", self.Sinks['AutoSink'])
        self.__commit_changes()

    def properties(self):
        properties = {}

        # Retrieve the properties form the sinks
        for sink in self.__sinks:
            properties[sink] = self.__sinks[sink].properties()
            properties[sink]['name'] = self.__sinks[sink].Name

        return properties

    def set_property(self, name, value):
        if name in self.__sinks:
            self.__sinks[name].update_properties(value)
        else:
            # Build a new sink
            self.__build_sink(name, self.Sinks[value['name']])
            # Then update it
            self.__sinks[name].update_properties(value)

    def sink(self):
        return self._tee

    def update_properties(self, properties):
        # Determinate the old sink that will be removed
        to_remove = set(self.__sinks.keys()).difference(properties.keys())
        self.__to_remove += to_remove

        # Update the properties
        super().update_properties(properties)

        # Commit all the changes (add/remove)
        self.__commit_changes()

    def dispose(self):
        for sink in self.__sinks.values():
            sink.dispose()

        self.__bus.remove_signal_watch()
        self.__bus.disconnect(self.__handler)

    def __build_sink(self, name, sink_class):
        outbin = Gst.Bin()
        queue = Gst.ElementFactory.make("queue", "queue")
        sink = sink_class(outbin)

        # Add and link
        outbin.add(queue)
        queue.link(sink.sink())

        # Set the bin ghost-pad
        outbin.add_pad(Gst.GhostPad.new("sink", queue.sinkpads[0]))

        # Add to the bin list and put it in the add-list
        self.__bins[name] = outbin
        self.__sinks[name] = sink
        self.__to_add.append(name)

    def __commit_changes(self):
        # Add all the new bins
        for name in self.__to_add:
            self.__add_sink(name)

        # Before removing old sinks, if in playing, the Pipeline need at last
        # one playing output or it cannot retrieve a new clock
        if len(self.__bins) - len(self.__to_add) - len(self.__to_remove) == 0:
            if self._state == Gst.State.PLAYING and len(self.__to_add) > 0:
                self.__wait_for_playing.acquire(False)
                self.__wait_for_playing.acquire()

        # Remove all the old bins
        for name in self.__to_remove:
            if len(self.__bins) > 1:
                self.__remove_sink(name)

        # Clear the lists
        self.__to_add.clear()
        self.__to_remove.clear()

    def __add_sink(self, name):
        outbin = self.__bins[name]

        # Add to pipeline
        self._pipe.add(outbin)

        # Set the bin in PAUSE to preroll
        if self._state != Gst.State.READY:
            outbin.set_state(Gst.State.PAUSED)

        # Get pad from the tee element and links it with the bin
        pad = self._tee.get_request_pad("src_%u")
        pad.link(outbin.sinkpads[0])

        # Add a reference to the request pad
        outbin.teepad = pad

    def __remove_sink(self, name):
        # Remove bin and sink form the respective list
        outbin = self.__bins.pop(name)
        sink = self.__sinks.pop(name)

        # Callback for the blocking probe
        def callback(pad, info, data):
            # Unlink and remove the bin
            self._tee.unlink(outbin)
            self._pipe.remove(outbin)

            # Release the tee srcpad
            self._tee.release_request_pad(outbin.teepad)

            # Set to NULL and uref the bin
            outbin.set_state(Gst.State.NULL)

            # Dispose the sink
            sink.dispose()

            return Gst.PadProbeReturn.REMOVE

        # Block the tee srcpad
        outbin.teepad.add_probe(Gst.PadProbeType.BLOCKING, callback, None)

    def __on_message(self, bus, message):
        if message.src == self._tee:
            self._state = message.parse_state_changed()[1]
        elif(message.parse_state_changed()[1] == Gst.State.PLAYING and
             message.src.parent in self.__bins.values() and
             self.__wait_for_playing.locked()):
                self.__wait_for_playing.release()
