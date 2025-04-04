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

from lisp.backend.media_element import MediaType
from lisp.core.properties import Property
from lisp.cues.media_cue import MediaCue
from lisp.plugins.gst_backend.gst_media import GstMedia


class GstMediaCue(MediaCue):
    media = Property(default=GstMedia.class_defaults())

    def __init__(self, app, media, id=None, pipeline=None):
        super().__init__(app, media, id=id)

        if pipeline is not None:
            media.pipe = pipeline


class GstCueFactory:
    def __init__(self, base_pipeline):
        self.base_pipeline = base_pipeline
        self.input = ""

    def __call__(self, app, id=None):
        return GstMediaCue(app, GstMedia(), id=id, pipeline=self.pipeline())

    def pipeline(self):
        if self.base_pipeline and self.input:
            return [self.input] + self.base_pipeline


class UriMediaCueFactory(GstCueFactory):
    def __init__(self, base_pipeline, media_type):
        super().__init__(base_pipeline)
        self.input = "UriInput"
        self.media_type = media_type

    def __call__(self, app, id=None, uri=None):
        cue = super().__call__(app, id=id)

        if uri is not None:
            try:
                cue.media.elements.UriInput.uri = uri
            except AttributeError:
                pass

        return cue


class CaptureAudioCueFactory(GstCueFactory):
    def __init__(self, base_pipeline):
        super().__init__(base_pipeline)
        self.input = "AutoSrc"
