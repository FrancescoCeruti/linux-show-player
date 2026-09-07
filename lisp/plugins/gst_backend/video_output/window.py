# This file is part of Linux Show Player
#
# Copyright 2026 Tobias Teichmann <tobias.teichmann@gmx.at>
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

import logging
import weakref
from collections import namedtuple
from typing import Optional, Tuple

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QColor, QGuiApplication, QScreen
from PyQt5.QtWidgets import QApplication, QWidget

from lisp.core.util import weak_call_proxy
from lisp.plugins.gst_backend.gi_repository import Gst
from lisp.plugins.gst_backend.gst_utils import GstError, gst_request_pad

logger = logging.getLogger(__name__)

_Channel = namedtuple(
    "_Channel", "intervideosrc queue videoconvert alpha_caps pad"
)


def _color_to_argb(color: QColor) -> int:
    return (
        (color.alpha() << 24)
        | (color.red() << 16)
        | (color.green() << 8)
        | color.blue()
    )


class VideoOutputWindow:
    """A persistent, borderless, always-present video output surface.

    Owns a frameless widget and a persistent GStreamer pipeline
    (``compositor ! videoconvert ! ximagesink``) that lives for as long as
    the window is open, independently of any cue's own pipeline. A solid
    color background is permanently linked into the compositor at the
    lowest z-order, so the window shows something meaningful even with no
    cue attached. Cues attach to the window dynamically, by channel name,
    via `request_channel`/`release_channel` - this is what allows several
    cues to render into (and be composited within) the same window at once.
    """

    def __init__(self, definition: dict):
        self._id = definition["id"]

        self._widget = None
        self._window_handle = None
        self._pipeline = None
        self._compositor = None
        self._background_bin = None
        self._background_src = None
        self._channels = {}

        self.background_color = QColor("#000000")
        self.update_definition(definition)

    def update_definition(self, definition: dict) -> None:
        self.name = definition.get("name", self._id)
        self.screen_name = definition.get("screen", "")
        self.fullscreen = definition.get("fullscreen", True)
        self.geometry = definition.get("geometry", [0, 0, 1280, 720])
        self.set_background_color(definition.get("background_color", "#000000"))

    def is_open(self) -> bool:
        return self._pipeline is not None

    def open(self) -> None:
        if self.is_open():
            return

        self._create_widget()
        self._create_pipeline()

        logger.info(f'Opened video output window "{self.name}"')

    def close(self) -> None:
        if not self.is_open():
            return

        for channel in list(self._channels):
            self.release_channel(channel)

        self._pipeline.set_state(Gst.State.NULL)
        self._pipeline.get_state(Gst.SECOND)

        self._pipeline = None
        self._compositor = None
        self._background_bin = None
        self._background_src = None

        if self._widget is not None:
            self._widget.close()
            self._widget.deleteLater()
            self._widget = None
        self._window_handle = None

        logger.info(f'Closed video output window "{self.name}"')

    def _create_widget(self) -> None:
        self._widget = QWidget(None, Qt.FramelessWindowHint | Qt.Window)
        self._widget.setWindowTitle(self.name)
        self._widget.setAttribute(Qt.WA_NativeWindow, True)
        self._widget.setStyleSheet("background: black;")

        screen = self._find_screen()
        if self.fullscreen:
            if screen is not None:
                self._widget.setGeometry(screen.geometry())
            self._widget.showFullScreen()
        else:
            x, y, w, h = self.geometry
            if screen is not None:
                origin = screen.geometry().topLeft()
                x += origin.x()
                y += origin.y()
            self._widget.setGeometry(QRect(x, y, w, h))
            self._widget.show()

        self._window_handle = int(self._widget.winId())

        # Force the widget's create/show to actually reach the X server
        # before GStreamer's tries to operate on the window id
        QApplication.processEvents()
        QApplication.processEvents()

    def _find_screen(self) -> Optional[QScreen]:
        for screen in QGuiApplication.screens():
            if screen.name() == self.screen_name:
                return screen
        return QGuiApplication.primaryScreen()

    def _output_size(self) -> Tuple[int, int]:
        if self.fullscreen:
            screen = self._find_screen()
            if screen is not None:
                geometry = screen.geometry()
                return geometry.width(), geometry.height()
            return 1280, 720

        return self.geometry[2], self.geometry[3]

    def set_background_color(self, color: str) -> None:
        self.background_color = QColor(color)
        if self._background_src is not None:
            self._background_src.set_property(
                "foreground-color", _color_to_argb(self.background_color)
            )

    def _create_pipeline(self) -> None:
        self._pipeline = Gst.Pipeline.new(f"video-output-{self._id}")

        self._compositor = Gst.ElementFactory.make("compositor", None)
        videoconvert = Gst.ElementFactory.make("videoconvert", None)
        sink = Gst.ElementFactory.make("ximagesink", None)

        self._pipeline.add(self._compositor)
        self._pipeline.add(videoconvert)
        self._pipeline.add(sink)
        self._compositor.link(videoconvert)
        videoconvert.link(sink)

        width, height = self._output_size()

        self._background_bin = Gst.parse_bin_from_description(
            "videotestsrc name=bg-src pattern=solid-color is-live=true ! "
            f"capsfilter caps=video/x-raw,width={width},height={height},"
            "framerate=25/1",
            True,
        )
        self._background_src = self._background_bin.get_by_name("bg-src")
        self._background_src.set_property(
            "foreground-color", _color_to_argb(self.background_color)
        )

        self._pipeline.add(self._background_bin)
        self._background_bin.get_static_pad("src").link(
            gst_request_pad(self._compositor)
        )

        bus = self._pipeline.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect(
            "sync-message::element",
            weak_call_proxy(weakref.WeakMethod(self._on_sync_message)),
        )
        bus.connect(
            "message::error",
            weak_call_proxy(weakref.WeakMethod(self._on_error)),
        )

        self._pipeline.set_state(Gst.State.PLAYING)

    def _on_sync_message(self, bus, message) -> None:
        structure = message.get_structure()
        if (
            structure is not None
            and structure.get_name() == "prepare-window-handle"
        ):
            if self._window_handle is not None:
                message.src.set_window_handle(self._window_handle)

    def _on_error(self, bus, message) -> None:
        error, debug = message.parse_error()
        logger.error(
            f'Video output window "{self.name}": {error}',
            exc_info=GstError(debug),
        )

    def request_channel(
        self, channel: str, geometry: Tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0)
    ) -> None:
        if not self.is_open() or channel in self._channels:
            return

        intervideosrc = Gst.ElementFactory.make("intervideosrc", None)
        intervideosrc.set_property("channel", channel)
        queue = Gst.ElementFactory.make("queue", None)  # Buffers stream since intervideosrc does not
        videoconvert = Gst.ElementFactory.make("videoconvert", None)
        alpha_caps = Gst.ElementFactory.make("capsfilter", None)
        alpha_caps.set_property(
            "caps", Gst.Caps.from_string("video/x-raw,format=AYUV")
        )
        chain = (intervideosrc, queue, videoconvert, alpha_caps)

        for element in chain:
            self._pipeline.add(element)
        intervideosrc.link(queue)
        queue.link(videoconvert)
        videoconvert.link(alpha_caps)

        pad = gst_request_pad(self._compositor)
        alpha_caps.get_static_pad("src").link(pad)

        width, height = self._output_size()
        pos_x, pos_y, scale_width, scale_height = geometry
        pad.set_property("xpos", round(pos_x * width))
        pad.set_property("ypos", round(pos_y * height))
        pad.set_property("width", round(scale_width * width))
        pad.set_property("height", round(scale_height * height))
        pad.set_property("sizing-policy", "keep-aspect-ratio")

        for element in chain:
            element.sync_state_with_parent()

        self._channels[channel] = _Channel(
            intervideosrc, queue, videoconvert, alpha_caps, pad
        )
        logger.debug(
            f'Video output window "{self.name}": channel "{channel}" attached'
        )

    def update_channel_geometry(
        self, channel: str, geometry: Tuple[float, float, float, float]
    ) -> None:
        entry = self._channels.get(channel)
        if entry is None:
            return

        width, height = self._output_size()
        pos_x, pos_y, scale_width, scale_height = geometry
        entry.pad.set_property("xpos", round(pos_x * width))
        entry.pad.set_property("ypos", round(pos_y * height))
        entry.pad.set_property("width", round(scale_width * width))
        entry.pad.set_property("height", round(scale_height * height))

    def release_channel(self, channel: str) -> None:
        entry = self._channels.pop(channel, None)
        if entry is None:
            return

        chain = (
            entry.intervideosrc,
            entry.queue,
            entry.videoconvert,
            entry.alpha_caps,
        )

        for element in chain:
            element.set_state(Gst.State.NULL)

        entry.alpha_caps.get_static_pad("src").unlink(entry.pad)
        self._compositor.release_request_pad(entry.pad)

        for element in chain:
            self._pipeline.remove(element)

        logger.debug(
            f'Video output window "{self.name}": channel "{channel}" released'
        )
