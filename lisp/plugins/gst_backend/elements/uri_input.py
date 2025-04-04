# This file is part of Linux Show Player
#
# Copyright 2024 Francesco Ceruti <ceppofrancy@gmail.com>
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

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.backend.media_element import MediaType, ElementType
from lisp.core.decorators import async_in_pool
from lisp.core.properties import Property
from lisp.core.session_uri import SessionURI
from lisp.plugins.gst_backend.gi_repository import Gst
from lisp.plugins.gst_backend.gst_element import GstSrcElement
from lisp.plugins.gst_backend.gst_properties import GstProperty, GstURIProperty
from lisp.plugins.gst_backend.gst_utils import gst_uri_duration

class UriInput(GstSrcElement):
    ElementType = ElementType.Input
    MediaType = MediaType.Unknown
    Name = QT_TRANSLATE_NOOP("MediaElementName", "URI Input")

    _mtime = Property(default=-1)
    uri = GstURIProperty("decoder", "uri")
    download = GstProperty("decoder", "download", default=False)
    buffer_size = GstProperty("decoder", "buffer-size", default=-1)
    use_buffering = GstProperty("decoder", "use-buffering", default=False)

    def __init__(self, pipeline):
        super().__init__(pipeline)

        self.decoder = Gst.ElementFactory.make("uridecodebin", None)
        self.audio_queue = Gst.ElementFactory.make("queue", "audio_queue")
        self.video_queue = Gst.ElementFactory.make("queue", "video_queue")
        self.audio_convert = Gst.ElementFactory.make("audioconvert", None)
        self.video_convert = Gst.ElementFactory.make("videoconvert", None)

        self._handler = self.decoder.connect("pad-added", self.__on_pad_added)

        self.pipeline.add(self.decoder)
        self.pipeline.add(self.audio_queue)
        self.pipeline.add(self.video_queue)
        self.pipeline.add(self.audio_convert)
        self.pipeline.add(self.video_convert)
        
        self.audio_queue.link(self.audio_convert)
        self.video_queue.link(self.video_convert)

        self.changed("uri").connect(self.__uri_changed)

    def input_uri(self) -> SessionURI:
        return SessionURI(self.uri)

    def dispose(self):
        self.decoder.disconnect(self._handler)

    def src(self):
        return self.audio_convert
    
    def __on_pad_added(self, *args):
        self.decoder.link(self.audio_queue)
        self.decoder.link(self.video_queue)

    def __uri_changed(self, uri):
        uri = SessionURI(uri)

        old_mtime = self._mtime
        if uri.is_local:
            # If the uri is a file update the current mtime
            path = Path(uri.absolute_path)
            if path.exists():
                self._mtime = path.stat().st_mtime
        else:
            old_mtime = None
            self._mtime = -1

        # If the file changed, or the duration is invalid
        if old_mtime != self._mtime or self.duration < 0:
            self.__duration()

    @async_in_pool(pool=ThreadPoolExecutor(1))
    def __duration(self):
        self.duration = gst_uri_duration(self.input_uri())
