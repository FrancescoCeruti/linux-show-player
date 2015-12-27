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

import os

from PyQt5.QtCore import QStandardPaths, Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QFileDialog, QApplication

from lisp import backends
from lisp.application import Application
from lisp.core.module import Module
from lisp.cues.cue_factory import CueFactory
from lisp.ui.mainwindow import MainWindow
from lisp.utils.configuration import config
from lisp.utils.util import qfile_filters


class LoadBackend(Module):
    """Load the default backend."""

    def __init__(self):
        super().__init__()
        backends.set_backend(config['Backend']['Default'])

        MainWindow().register_cue_menu_action('Media cue (from file)',
                                              self.add_uri_audio_media_cue,
                                              category='Media cues',
                                              shortcut='CTRL+M')

    # Function to be registered in the mainWindow
    @staticmethod
    def add_uri_audio_media_cue():
        path = QStandardPaths.writableLocation(QStandardPaths.MusicLocation)

        extensions = backends.backend().supported_extensions()
        filters = qfile_filters(extensions, anyfile=False)
        files, _ = QFileDialog.getOpenFileNames(MainWindow(), 'Choose files',
                                                path, filters)

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

        for file in files:
            cue = CueFactory.create_cue('URIAudioCue', uri='file://' + file)
            # Use the filename without extension as cue name
            cue.name = os.path.splitext(os.path.basename(file))[0]
            Application().cue_model.add(cue)

        QApplication.restoreOverrideCursor()