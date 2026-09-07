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

import uuid
from typing import Optional, TYPE_CHECKING

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp import backend
from lisp.backend.media_element import ElementType, MediaType
from lisp.core.properties import Property
from lisp.plugins.gst_backend.gi_repository import Gst
from lisp.plugins.gst_backend.gst_element import GstMediaElement

if TYPE_CHECKING:
    from lisp.plugins.gst_backend.video_output.manager import (
        VideoOutputWindowManager,
    )


class PipGeometryProperty(Property):
    """A Property that also pushes live updates to the compositor pad.

    Mirrors `GstProperty`'s "always push through immediately" behaviour
    (see `gst_properties.py`), but the actual `Gst.Pad` this maps to is
    owned by the target `VideoOutputWindow`'s own pipeline and only exists
    while the channel is attached, so the push goes through the window
    manager instead of a directly-held element reference.
    """

    def __set__(self, instance, value):
        super().__set__(instance, value)
        if instance is not None:
            instance._push_geometry()


class VideoOutput(GstMediaElement):
    """Sends video into a named, persistent output window.

    Unlike `AutoSink`/`WaylandSink`, this element does not own a display
    surface itself: it only feeds an `intervideosink` channel that the
    target `VideoOutputWindow`'s own persistent pipeline picks up (see
    `lisp.plugins.gst_backend.video_output`). This is what allows the
    window to outlive this cue's pipeline, and to have several cues render
    into it (or into other windows) at the same time.
    """

    ElementType = ElementType.Output
    MediaType = MediaType.Video
    Name = QT_TRANSLATE_NOOP("MediaElementName", "Video Output Window")

    window_id = Property(default="")
    window_name = Property(default="")

    # Normalized (0.0-1.0) position/size
    pos_x = PipGeometryProperty(default=0.0)
    pos_y = PipGeometryProperty(default=0.0)
    scale_width = PipGeometryProperty(default=1.0)
    scale_height = PipGeometryProperty(default=1.0)

    def __init__(self, pipeline):
        super().__init__(pipeline)

        self.channel = f"lsp-video-{uuid.uuid4().hex}"

        self.intervideosink = Gst.ElementFactory.make("intervideosink", None)
        self.intervideosink.set_property("channel", self.channel)
        self.pipeline.add(self.intervideosink)

    def sink(self) -> Gst.Element:
        return self.intervideosink

    def play(self) -> None:
        manager = self._manager()
        if manager is not None:
            manager.add_channel(
                self.window_id,
                self.window_name,
                self.channel,
                (self.pos_x, self.pos_y, self.scale_width, self.scale_height),
                self._on_window_closed,
            )

    def stop(self) -> None:
        self._detach()

    def dispose(self) -> None:
        self._detach()
        self.pipeline.remove(self.intervideosink)

    def _detach(self) -> None:
        manager = self._manager()
        if manager is not None:
            manager.remove_channel(self.channel)

    def _push_geometry(self) -> None:
        manager = self._manager()
        if manager is not None:
            manager.update_channel_geometry(
                self.channel,
                (self.pos_x, self.pos_y, self.scale_width, self.scale_height),
            )

    def _on_window_closed(self) -> None:
        cue = self._owning_cue()
        if cue is not None:
            cue.stop()
            return

        media = self._owning_media()
        if media is not None:
            media.stop()

    def _owning_media(self):
        media_ref = getattr(self.pipeline, "lsp_media", None)
        return media_ref() if media_ref is not None else None

    def _owning_cue(self):
        media = self._owning_media()
        if media is None:
            return None
        cue_ref = getattr(media, "lsp_cue", None)
        return cue_ref() if cue_ref is not None else None

    @staticmethod
    def _manager() -> Optional["VideoOutputWindowManager"]:
        gst_backend = backend.get_backend()
        return getattr(gst_backend, "video_outputs", None)
