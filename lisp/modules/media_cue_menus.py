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

import os

from PyQt5.QtCore import QStandardPaths, Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QFileDialog, QApplication, QMessageBox

from lisp.backend import get_backend
from lisp.application import Application
from lisp.core.module import Module
from lisp.cues.cue_factory import CueFactory
from lisp.ui.mainwindow import MainWindow
from lisp.ui.ui_utils import qfile_filters, translate


class MediaCueMenus(Module):
    """Register menus to add MediaCue to layouts"""

    def __init__(self):
        MainWindow().register_cue_menu_action(
            translate('MediaCueMenus', 'Audio cue (from file)'),
            self.add_uri_audio_media_cue,
            category='Media cues',
            shortcut='CTRL+M')

    @staticmethod
    def add_uri_audio_media_cue():
        """Add audio MediaCue(s) form user-selected files"""

        if get_backend() is None:
            QMessageBox.critical(MainWindow(), 'Error', 'Backend not loaded')
            return

        # Default path to system "music" folder
        path = QStandardPaths.writableLocation(QStandardPaths.MusicLocation)

        # Get the backend extensions and create a filter for the Qt file-dialog
        extensions = get_backend().supported_extensions()
        filters = qfile_filters(extensions, anyfile=False)
        # Display a file-dialog for the user to choose the media-files
        files, _ = QFileDialog.getOpenFileNames(MainWindow(),
                                                translate('MediaCueMenus',
                                                          'Select media files'),
                                                path, filters)

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

        # Create media cues, and add them to the Application cue_model
        for file in files:
            cue = CueFactory.create_cue('URIAudioCue', uri='file://' + file)
            # Use the filename without extension as cue name
            cue.name = os.path.splitext(os.path.basename(file))[0]
            Application().cue_model.add(cue)

        QApplication.restoreOverrideCursor()
