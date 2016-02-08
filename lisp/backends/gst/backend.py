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

from lisp.backends.base.backend import Backend as BaseBackend
from lisp.backends.gst import elements, settings
from lisp.backends.gst.gi_repository import Gst, GObject
from lisp.backends.gst.gst_cue_factories import register_factories
from lisp.backends.gst.gst_media_settings import GstMediaSettings
from lisp.backends.gst.gst_settings import GstSettings
from lisp.backends.gst.gst_utils import gst_parse_tag_list
from lisp.backends.gst.gst_utils import gst_uri_metadata, gst_mime_types, \
    gst_uri_duration
from lisp.cues.media_cue import MediaCue
from lisp.ui.settings.app_settings import AppSettings
from lisp.ui.settings.cue_settings import CueSettingsRegistry


class Backend(BaseBackend):
    def __init__(self):
        """Startup GStreamer and GObject."""

        # Initialize GStreamer and GObject
        GObject.threads_init()
        Gst.init(None)

        # Register GStreamer settings widgets
        AppSettings.register_settings_widget(GstSettings)
        # Add MediaCue settings widget to the CueLayout
        CueSettingsRegistry().add_item(GstMediaSettings, MediaCue)
        # Register the GstMedia cue builder
        register_factories()

        elements.load()
        settings.load()

    def uri_duration(self, uri):
        return gst_uri_duration(uri)

    def uri_tags(self, uri):
        return gst_parse_tag_list(gst_uri_metadata(uri).get_tags())

    def supported_extensions(self):
        # TODO: cache
        extensions = {'audio': [], 'video': []}

        for gst_mime, gst_extensions in gst_mime_types():
            for mime in ['audio', 'video']:
                if gst_mime.startswith(mime):
                    extensions[mime].extend(gst_extensions)

        return extensions
