# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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
from os import path
from urllib.parse import quote as urlquote, unquote as urlunquote

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.application import Application
from lisp.backend.media_element import MediaType
from lisp.core.decorators import async_in_pool
from lisp.core.properties import Property
from lisp.plugins.gst_backend.gi_repository import Gst
from lisp.plugins.gst_backend.gst_element import GstProperty, GstSrcElement
from lisp.plugins.gst_backend.gst_utils import gst_uri_duration


def abs_path(path_):
    return Application().session.abs_path(path_)


def uri_split(uri):
    try:
        scheme, path = uri.split("://")
    except ValueError:
        scheme = path = ""

    return scheme, path


def uri_adapter(uri):
    scheme, path = uri_split(uri)
    return scheme + "://" + urlquote(abs_path(path))


class UriInput(GstSrcElement):
    MediaType = MediaType.Audio
    Name = QT_TRANSLATE_NOOP("MediaElementName", "URI Input")

    _mtime = Property(default=-1)
    uri = GstProperty("decoder", "uri", default="", adapter=uri_adapter)
    download = GstProperty("decoder", "download", default=False)
    buffer_size = GstProperty("decoder", "buffer-size", default=-1)
    use_buffering = GstProperty("decoder", "use-buffering", default=False)

    def __init__(self, pipeline):
        super().__init__(pipeline)

        self.decoder = Gst.ElementFactory.make("uridecodebin", None)
        self.audio_convert = Gst.ElementFactory.make("audioconvert", None)
        self._handler = self.decoder.connect("pad-added", self.__on_pad_added)

        self.pipeline.add(self.decoder)
        self.pipeline.add(self.audio_convert)

        self.changed("uri").connect(self.__uri_changed)
        Application().session.changed("session_file").connect(
            self.__session_moved
        )

    def input_uri(self):
        return self.uri

    def dispose(self):
        self.decoder.disconnect(self._handler)

    def src(self):
        return self.audio_convert

    def __on_pad_added(self, *args):
        self.decoder.link(self.audio_convert)

    def __uri_changed(self, uri):
        # Save the current mtime (file flag for last-change time)
        mtime = self._mtime

        # If the uri is a file update the current mtime
        scheme, path_ = uri_split(uri)
        if scheme == "file":
            path_ = abs_path(path_)
            if path.exists(path_):
                self._mtime = path.getmtime(path_)
        else:
            mtime = None

        # If something is changed or the duration is invalid
        if mtime != self._mtime or self.duration < 0:
            self.__duration()

    @async_in_pool(pool=ThreadPoolExecutor(1))
    def __duration(self):
        scheme, path = uri_split(self.uri)
        self.duration = gst_uri_duration(scheme + "://" + abs_path(path))

    def __session_moved(self, _):
        scheme, path_ = uri_split(self.decoder.get_property("uri"))
        if scheme == "file":
            path_ = urlunquote(path_)
            self.uri = "file://" + Application().session.rel_path(path_)
