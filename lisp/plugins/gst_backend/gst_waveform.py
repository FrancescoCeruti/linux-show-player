# This file is part of Linux Show Player
#
# Copyright 2020 Francesco Ceruti <ceppofrancy@gmail.com>
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

import audioop
import logging
from array import array

from lisp.backend.waveform import Waveform
from .gi_repository import Gst, GLib
from .gst_utils import GstError

logger = logging.getLogger(__name__)


class GstWaveform(Waveform):
    """Waveform container."""

    PIPELINE_TEMPLATE = (
        'uridecodebin uri="{uri}" '
        "! audioconvert ! audio/x-raw, format=S16LE "
        "! audiobuffersplit output-buffer-duration={sample_length} "
        "! appsink name=app_sink emit-signals=true sync=false"
    )
    MAX_S16_PCM_VALUE = 32768

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pipeline = None
        self._bus_id = None

        self._temp_peak = array("i")
        self._temp_rms = array("i")

    def _load_waveform(self):
        # Make sure we start from zero
        self._clear()

        # Create the pipeline with an appropriate buffer-size to control
        # how many seconds of data we receive at each 'new-sample' event.
        try:
            self._pipeline = Gst.parse_launch(
                self.PIPELINE_TEMPLATE.format(
                    uri=self._uri.uri,
                    sample_length=f"{self.duration // 1000}/{self.max_samples}",
                )
            )
        except GLib.GError:
            logger.warning(
                f'Cannot generate waveform for "{self._uri.unquoted_uri}"',
                exc_info=True
            )
            return True

        # Connect to the app-sink
        app_sink = self._pipeline.get_by_name("app_sink")
        app_sink.connect("new-sample", self._on_new_sample, app_sink)

        # Watch the event bus
        bus = self._pipeline.get_bus()
        bus.add_signal_watch()
        self._bus_id = bus.connect("message", self._on_bus_message)

        # Start the pipeline
        self._pipeline.set_state(Gst.State.PLAYING)

        return False

    def clear(self):
        super().clear()
        self._clear()

    def _clear(self):
        if self._pipeline is not None:
            # Stop the pipeline
            self._pipeline.set_state(Gst.State.NULL)

            if self._bus_id is not None:
                # Disconnect from the bus
                bus = self._pipeline.get_bus()
                bus.remove_signal_watch()
                bus.disconnect(self._bus_id)

        self._bus_id = None
        self._pipeline = None

        self._temp_peak = array("i")
        self._temp_rms = array("i")

    def _on_new_sample(self, sink, _):
        """Called by GStreamer every time we have a new sample ready."""
        buffer = sink.emit("pull-sample").get_buffer()
        if buffer is not None:
            # Get the all data from the buffer, as bytes
            # We expect each audio sample to be 16bits signed integer
            data_bytes = buffer.extract_dup(0, buffer.get_size())
            # Get the max of the absolute values in the samples
            self._temp_peak.append(audioop.max(data_bytes, 2))
            # Get rms of the samples
            self._temp_rms.append(audioop.rms(data_bytes, 2))

        return Gst.FlowReturn.OK

    def _on_bus_message(self, bus, message):
        if message.type == Gst.MessageType.EOS:
            self._eos()
        elif message.type == Gst.MessageType.ERROR:
            error, debug = message.parse_error()
            logger.warning(
                f'Cannot generate waveform for "{self._uri.unquoted_uri}": {error.message}',
                exc_info=GstError(debug),
            )

            self._clear()
            self.failed.emit()

    def _eos(self):
        """Called when the file has been processed."""
        self.peak_samples = []
        self.rms_samples = []

        # Normalize data
        for peak, rms in zip(self._temp_peak, self._temp_rms):
            self.peak_samples.append(
                round(peak / self.MAX_S16_PCM_VALUE, self.MAX_DECIMALS)
            )
            self.rms_samples.append(
                round(rms / self.MAX_S16_PCM_VALUE, self.MAX_DECIMALS)
            )

        # Dump the data into a file (does nothing if caching is disabled)
        self._to_cache()
        # Clear leftovers
        self._clear()

        # Notify that the waveform data are ready
        self.ready.emit()
