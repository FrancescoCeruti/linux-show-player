# This file is part of Linux Show Player
#
# Copyright 2021 Francesco Ceruti <ceppofrancy@gmail.com>
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

from threading import Event

from lisp.core.properties import Property
from lisp.core.session_uri import SessionURI

from .gi_repository import GstController, Gst


class GstProperty(Property):
    def __init__(
        self, element_name, property_name, default=None, adapter=None, **meta
    ):
        super().__init__(default=default, **meta)
        self.element_name = element_name
        self.property_name = property_name
        self.adapter = adapter

    def __set__(self, instance, value):
        super().__set__(instance, value)

        if instance is not None:
            if self.adapter is not None:
                value = self.adapter(value)

            element = getattr(instance, self.element_name)
            element.set_property(self.property_name, value)


class GstURIProperty(GstProperty):
    def __init__(self, element_name, property_name, **meta):
        super().__init__(
            element_name,
            property_name,
            default="",
            adapter=self._adapter,
            **meta,
        )

    def __set__(self, instance, value):
        super().__set__(instance, SessionURI(value))

    def __get__(self, instance, owner=None):
        value = super().__get__(instance, owner)
        if isinstance(value, SessionURI):
            if value.is_local:
                return value.relative_path
            else:
                return value.uri

        return value

    def _adapter(self, value: SessionURI):
        return value.uri


class GstLiveProperty(Property):
    def __init__(self, element_name, property_name, adapter=None, **meta):
        super().__init__(**meta)
        self.element_name = element_name
        self.property_name = property_name
        self.adapter = adapter

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            element = getattr(instance, self.element_name)
            return element.get_property(self.property_name)

    def __set__(self, instance, value):
        if self.adapter is not None:
            value = self.adapter(value)

        element = getattr(instance, self.element_name)
        element.set_property(self.property_name, value)


class GstPropertyController:
    """Control a Gst.Element (controllable) property.

    This class leverage the GstController "lib" functionalities, allowing
    their usage in a "live" context where timing and values must be determined
    on the fly.

    To achieve this behavior an "identy" element (sync_element) is used to
    synchronize the user "request" with the actual pipeline processing.

    For this mechanism to work correctly there should not be any significant
    buffering in upstream elements (e.g. queues).
    """

    def __init__(
        self,
        pipeline: Gst.Pipeline,
        element: Gst.Element,
        sync_element: Gst.Element,
        property_name: str,
        interpolation_mode: int = GstController.InterpolationMode.CUBIC_MONOTONIC,
    ):
        self._pipeline = pipeline
        self._element = element
        self._sync_element = sync_element
        self._property_name = property_name

        self._sync_event = Event()
        self._control_points = {}
        self._delay = 0

        self._control_source = GstController.InterpolationControlSource.new()
        self._control_source.set_property("mode", interpolation_mode)

        self._control_binding = GstController.DirectControlBinding.new_absolute(
            self._element, self._property_name, self._control_source
        )
        self._element.add_control_binding(self._control_binding)

    @property
    def delay(self):
        return self._delay

    def set(self, control_points: dict):
        """Set the control points to be used to change the value."""
        self._control_points = control_points
        self._delay = 0

        self._sync_event.clear()

        # Connect the "handoff" signal.
        # The callback will be called the next time a buffer is "processed"
        # by the sync_element, we make control_points available to the callback
        handle = self._sync_element.connect("handoff", self._set_control_points)

        # Wait for the callback to set the flag.
        # A timeout is set to avoid deadlocking if the callback is never called,
        # this might happen if there are no more buffers to process.
        self._sync_event.wait(1)

        # Disconnect the callback, we only need to call it once
        self._sync_element.disconnect(handle)

    def reset(self):
        self._control_source.unset_all()
        self._control_points.clear()

    def _set_control_points(self, element: Gst.Element, buffer: Gst.Buffer):
        if not self._sync_event.is_set():
            try:
                start = buffer.pts

                # Calculate the difference between the buffer timestamp and the
                # current time, this allows precise timing (e.g. for fadeout)
                self._calc_sync_delay(start)

                self._control_source.unset_all()

                for time, value in self._control_points.items():
                    self._control_source.set(start + time * Gst.MSECOND, value)
            finally:
                # Inform the thread that called the `set()` method that we have
                # set the control points
                self._sync_event.set()

    def _calc_sync_delay(self, start):
        ok, position = self._pipeline.query_position(Gst.Format.TIME)
        self._delay = (start - position) // Gst.MSECOND
