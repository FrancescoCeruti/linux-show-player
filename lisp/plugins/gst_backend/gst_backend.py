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
from lisp.cues.cue_factory import CueFactory

from lisp import backend
from lisp.backend.backend import Backend as BaseBackend
from lisp.core.decorators import memoize
from lisp.core.plugin import Plugin
from lisp.cues.media_cue import MediaCue
from lisp.plugins.gst_backend import elements, settings
from lisp.plugins.gst_backend.gi_repository import Gst
from lisp.plugins.gst_backend.gst_cue_factories import gst_media_cue_factory,\
    UriAudioCueFactory, CaptureAudioCueFactory
from lisp.plugins.gst_backend.gst_media_settings import GstMediaSettings
from lisp.plugins.gst_backend.gst_settings import GstSettings
from lisp.plugins.gst_backend.gst_utils import gst_parse_tags_list, \
    gst_uri_metadata, gst_mime_types, gst_uri_duration
from lisp.ui.settings.app_settings import AppSettings
from lisp.ui.settings.cue_settings import CueSettingsRegistry


class GstBackend(Plugin, BaseBackend):

    Name = 'GStreamer Backend'
    Authors = ('Francesco Ceruti', )
    Description = 'Provide audio playback capabilities via the GStreamer ' \
                  'framework'

    def __init__(self, app):
        super().__init__(app)

        # Initialize GStreamer
        Gst.init(None)

        # Register GStreamer settings widgets
        AppSettings.register_settings_widget(GstSettings, GstBackend.Config)
        # Add MediaCue settings widget to the CueLayout
        CueSettingsRegistry().add_item(GstMediaSettings, MediaCue)

        # Register the GstMediaCue factories
        base_pipeline = GstBackend.Config['Pipeline']

        CueFactory.register_factory('MediaCue', gst_media_cue_factory)
        CueFactory.register_factory(
            'URIAudioCue', UriAudioCueFactory(base_pipeline))
        CueFactory.register_factory(
            'CaptureAudioCue', CaptureAudioCueFactory(base_pipeline))

        elements.load()
        settings.load()

        backend.set_backend(self)

    def uri_duration(self, uri):
        return gst_uri_duration(uri)

    def uri_tags(self, uri):
        tags = gst_uri_metadata(uri).get_tags()
        if tags is not None:
            return gst_parse_tags_list(tags)

        return {}

    @memoize
    def supported_extensions(self):
        extensions = {'audio': [], 'video': []}

        for gst_mime, gst_extensions in gst_mime_types():
            for mime in ['audio', 'video']:
                if gst_mime.startswith(mime):
                    extensions[mime].extend(gst_extensions)

        return extensions
