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
from lisp.backends.gst.gi_repository import Gst
from lisp.backends.gst.gst_element import GstMediaElement, GstProperty


class UriInput(GstMediaElement):
    ElementType = ElementType.Input
    MediaType = MediaType.Audio
    Name = "URIInput"

    uri = GstProperty('decoder', default='')
    download = GstProperty('decoder', default=False)
    buffer_size = GstProperty('decoder', default=-1, gst_name='buffer-size')
    use_buffering = GstProperty('decoder', default=False,
                                gst_name='use-buffering')

    def __init__(self, pipe):
        super().__init__()

        self.decoder = Gst.ElementFactory.make("uridecodebin", None)
        self.audio_convert = Gst.ElementFactory.make("audioconvert", None)
        self._handler = self.decoder.connect("pad-added", self.__on_pad_added)

        pipe.add(self.decoder)
        pipe.add(self.audio_convert)

    def input_uri(self):
        return self.uri

    def dispose(self):
        self.decoder.disconnect(self._handler)

    def src(self):
        return self.audio_convert

    def __on_pad_added(self, *args):
        self.decoder.link(self.audio_convert)
