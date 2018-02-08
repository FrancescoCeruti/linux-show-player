# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2018 Francesco Ceruti <ceppofrancy@gmail.com>
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

import os.path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QFileDialog, QApplication
from lisp.ui.ui_utils import translate, qfile_filters

from lisp import backend
from lisp.backend.backend import Backend as BaseBackend
from lisp.core.decorators import memoize
from lisp.core.plugin import Plugin
from lisp.cues.cue_factory import CueFactory
from lisp.cues.media_cue import MediaCue
from lisp.plugins.gst_backend import elements, settings
from lisp.plugins.gst_backend.gi_repository import Gst
from lisp.plugins.gst_backend.gst_media_cue import GstCueFactory, \
    UriAudioCueFactory
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

        # Register GstMediaCue factory
        CueFactory.register_factory('GstMediaCue', GstCueFactory(tuple()))

        # Add Menu entry
        self.app.window.register_cue_menu_action(
            translate('GstBackend', 'Audio cue (from file)'),
            self._add_uri_audio_cue,
            category='Media cues',
            shortcut='CTRL+M'
        )

        # Load elements and their settings-widgets
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

    def _add_uri_audio_cue(self):
        """Add audio MediaCue(s) form user-selected files"""

        files, _ = QFileDialog.getOpenFileNames(
            self.app.window,
            translate('GstBackend', 'Select media files'),
            self.app.session.path(),
            qfile_filters(self.supported_extensions(), anyfile=True)
        )

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

        # Create media cues, and add them to the Application cue_model
        factory = UriAudioCueFactory(GstBackend.Config['pipeline'])

        for file in files:
            file = self.app.session.rel_path(file)
            cue = factory(uri='file://' + file)
            # Use the filename without extension as cue name
            cue.name = os.path.splitext(os.path.basename(file))[0]
            self.app.cue_model.add(cue)

        QApplication.restoreOverrideCursor()