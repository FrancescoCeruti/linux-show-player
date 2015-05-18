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

from lisp.backends.base.media_cue_factory import MediaCueFactory
from lisp.backends.gst.gst_media import GstMedia
from lisp.cues.media_cue import MediaCue
from lisp.utils.configuration import config

__all__ = ['GstMediaFactory']


class GstMediaCueFactory(MediaCueFactory):
    MEDIA_TYPES = dict(config['GstMediaTypes'])

    @classmethod
    def create_cue(cls, media_type=None):
        pipe = GstMediaCueFactory.MEDIA_TYPES.get(media_type.lower(), None)

        if pipe is None:
            raise ValueError('Unsupported media type: {0}'.format(media_type))

        media = GstMedia()
        media.pipe = pipe

        return MediaCue(media)
