# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.backend.media_element import MediaType
from lisp.core.decorators import async_in_pool
from lisp.core.has_properties import Property
from lisp.modules.gst_backend.gi_repository import Gst
from lisp.modules.gst_backend.gst_element import GstProperty, \
    GstSrcElement
from lisp.modules.gst_backend.gst_utils import gst_uri_duration


class UriInput(GstSrcElement):
    MediaType = MediaType.Audio
    Name = QT_TRANSLATE_NOOP('MediaElementName', 'URI Input')

    uri = GstProperty('decoder', default='')
    download = GstProperty('decoder', default=False)
    buffer_size = GstProperty('decoder', default=-1, gst_name='buffer-size')
    use_buffering = GstProperty('decoder', default=False,
                                gst_name='use-buffering')
    _mtime = Property(default=-1)

    def __init__(self, pipe):
        super().__init__()

        self.decoder = Gst.ElementFactory.make("uridecodebin", None)
        self.audio_convert = Gst.ElementFactory.make("audioconvert", None)
        self._handler = self.decoder.connect("pad-added", self.__on_pad_added)

        pipe.add(self.decoder)
        pipe.add(self.audio_convert)

        self.changed('uri').connect(self.__uri_changed)

    def input_uri(self):
        return self.uri

    def dispose(self):
        self.decoder.disconnect(self._handler)

    def src(self):
        return self.audio_convert

    def __on_pad_added(self, *args):
        self.decoder.link(self.audio_convert)

    def __uri_changed(self, value):
        # Save the current mtime (file flag for last-change time)
        mtime = self._mtime
        # If the uri is a file, then update the current mtime
        if value.split('://')[0] == 'file':
            if path.exists(value.split('//')[1]):
                self._mtime = path.getmtime(value.split('//')[1])
        else:
            mtime = None

        # If something is changed or the duration is invalid
        if mtime != self._mtime or self.duration < 0:
            self.__duration()

    @async_in_pool(pool=ThreadPoolExecutor(1))
    def __duration(self):
        self.duration = gst_uri_duration(self.uri)
