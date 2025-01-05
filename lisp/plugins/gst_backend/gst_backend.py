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

import os.path

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QFileDialog, QApplication

from lisp import backend
from lisp.backend.backend import Backend as BaseBackend
from lisp.backend.media_element import MediaType
from lisp.command.layout import LayoutAutoInsertCuesCommand
from lisp.core.decorators import memoize
from lisp.core.plugin import Plugin
from lisp.cues.media_cue import MediaCue
from lisp.plugins.gst_backend import config, elements, settings
from lisp.plugins.gst_backend.gi_repository import Gst
from lisp.plugins.gst_backend.gst_media_cue import (
    GstCueFactory,
    UriMediaCueFactory,
)
from lisp.plugins.gst_backend.gst_media_settings import GstMediaSettings
from lisp.plugins.gst_backend.gst_settings import GstSettings
from lisp.plugins.gst_backend.gst_utils import (
    gst_parse_tags_list,
    gst_uri_metadata,
    gst_mime_types,
    gst_uri_duration,
)
from lisp.plugins.gst_backend.gst_waveform import GstWaveform
from lisp.ui.settings.app_configuration import AppConfigurationDialog
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.ui_utils import translate, qfile_filters


class GstBackend(Plugin, BaseBackend):
    Name = "GStreamer Backend"
    Authors = ("Francesco Ceruti",)
    Description = (
        "Provide audio playback capabilities via the GStreamer " "framework"
    )

    def __init__(self, app):
        super().__init__(app)

        # Initialize GStreamer
        Gst.init(None)
        # Register GStreamer settings widgets
        AppConfigurationDialog.registerSettingsPage(
            "plugins.gst", GstSettings, GstBackend.Config
        )
        # Register elements' application-level config
        for name, page in config.load():
            AppConfigurationDialog.registerSettingsPage(
                f"plugins.gst.{name}", page, GstBackend.Config
            )
        # Add MediaCue settings widget to the CueLayout
        CueSettingsRegistry().add(GstMediaSettings, MediaCue)

        # Register GstMediaCue factory
        app.cue_factory.register_factory("GstMediaCue", GstCueFactory(tuple()))
        # Add Menu entries
        self.app.window.registerCueMenu(
            translate("GstBackend", "Audio cue (from file)"),
            self._add_uri_audio_cue,
            category=QT_TRANSLATE_NOOP("CueCategory", "Media cues"),
            shortcut="CTRL+M",
        )
        self.app.window.registerCueMenu(
            translate("GstBackend", "Video cue (from file)"),
            self._add_uri_video_cue,
            category=QT_TRANSLATE_NOOP("CueCategory", "Media cues"),
            shortcut="CTRL+SHIFT+M",
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
        extensions = {"audio": [], "video": []}

        for gst_mime, gst_extensions in gst_mime_types():
            for mime in ["audio", "video"]:
                if gst_mime.startswith(mime):
                    extensions[mime].extend(gst_extensions)

        return extensions

    def uri_waveform(self, uri, duration=None):
        if duration is None or duration <= 0:
            duration = self.uri_duration(uri)

        return GstWaveform(
            uri,
            duration,
            cache_dir=self.app.conf.get("cache.position", ""),
        )

    def _add_uri_video_cue(self):
        # Create media cues, and add them to the Application cue_model
        extensions = self.supported_extensions()
        self._add_uri_cue({"video": extensions["video"]})
        
    def _add_uri_audio_cue(self):
        # Create media cues, and add them to the Application cue_model
        extensions = self.supported_extensions()
        self._add_uri_cue({"audio": extensions["audio"]})

    def _add_uri_cue(self, extensions):
        """Add audio MediaCue(s) form user-selected files"""
        # Get the last visited directory, or use the session-file location
        directory = GstBackend.Config.get("mediaLookupDir", "")
        if not os.path.exists(directory):
            directory = self.app.session.dir()

        # Open a filechooser, at the last visited directory
        files, _ = QFileDialog.getOpenFileNames(
            self.app.window,
            translate("GstBackend", "Select media files"),
            directory,
            qfile_filters(extensions, anyfile=True),
        )

        if files:
            # Updated the last visited directory
            GstBackend.Config["mediaLookupDir"] = os.path.dirname(files[0])
            GstBackend.Config.write()

            self.add_cue_from_files(files)

    def add_cue_from_urls(self, urls):
        extensions = self.supported_extensions()
        extensions = extensions["audio"] + extensions["video"]
        files = []

        for url in urls:
            # Get the file extension without the leading dot
            extension = os.path.splitext(url.fileName())[-1][1:]
            # If is a supported audio/video file keep it
            if extension in extensions:
                files.append(url.path())

        self.add_cue_from_files(files)

    def add_cue_from_files(self, files):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        extensions = self.supported_extensions()
        cues = []
        for file in files:
            # Get the file extension without the leading dot
            extension = os.path.splitext(file)[-1][1:]
            if extension in extensions['audio']:
                factory = UriMediaCueFactory(GstBackend.Config["audio-pipeline"], MediaType.Audio)
            elif extension in extensions['video']:
                factory = UriMediaCueFactory(GstBackend.Config["video-pipeline"], MediaType.Video)
            cue = factory(self.app, uri=file)
            # Use the filename without extension as cue name
            cue.name = os.path.splitext(os.path.basename(file))[0]

            cues.append(cue)

        # Insert the cue into the layout
        self.app.commands_stack.do(
            LayoutAutoInsertCuesCommand(self.app.session.layout, *cues)
        )

        QApplication.restoreOverrideCursor()
