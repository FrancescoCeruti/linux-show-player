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

from urllib.request import unquote

from PyQt5 import QtCore
from PyQt5.QtWidgets import QAction, QMessageBox, QDialog, QVBoxLayout, \
    QTreeWidget, QAbstractItemView, QDialogButtonBox, QTreeWidgetItem
from PyQt5.QtWidgets import QHeaderView

from lisp.application import Application
from lisp.modules.gst_backend.gst_utils import gst_uri_metadata, \
    gst_parse_tags_list
from lisp.core.module import Module
from lisp.cues.media_cue import MediaCue
from lisp.layouts.cue_layout import CueLayout
from lisp.ui.mainwindow import MainWindow
from lisp.ui.ui_utils import translate


class MediaInfo(Module):
    Name = 'MediaInfo'

    def __init__(self):
        self.menuAction = QAction(None)
        self.menuAction.triggered.connect(self.show_info)
        self.menuAction.setText(translate('MediaInfo', 'Media Info'))

        CueLayout.cm_registry.add_separator(MediaCue)
        CueLayout.cm_registry.add_item(self.menuAction, MediaCue)

    def show_info(self, clicked):
        media_uri = Application().layout.get_context_cue().media.input_uri()
        if not media_uri:
            QMessageBox.critical(MainWindow(), translate('MediaInfo', 'Error'),
                                 translate('MediaInfo', 'No info to display'))
        else:
            gst_info = gst_uri_metadata(media_uri)
            info = {'URI': unquote(gst_info.get_uri())}

            # Audio streams info
            for stream in gst_info.get_audio_streams():
                name = stream.get_stream_type_nick().capitalize()
                info[name] = {
                    'Bitrate': str(stream.get_bitrate() // 1000) + ' Kb/s',
                    'Channels': str(stream.get_channels()),
                    'Sample rate': str(stream.get_sample_rate()) + ' Hz',
                    'Sample size': str(stream.get_depth()) + ' bit'
                }

            # Video streams info
            for stream in gst_info.get_video_streams():
                name = stream.get_stream_type_nick().capitalize()
                info[name] = {
                    'Height': str(stream.get_height()) + ' px',
                    'Width': str(stream.get_width()) + ' px',
                    'Framerate': str(round(stream.get_framerate_num() /
                                           stream.get_framerate_denom()))
                }

            # Media tags
            info['Tags'] = {}

            tags = gst_info.get_tags()
            if tags is not None:
                tags = gst_parse_tags_list(tags)
                for tag in tags:
                    if type(tags[tag]).__str__ is not object.__str__:
                        info['Tags'][tag.capitalize()] = str(tags[tag])

            if not info['Tags']:
                info.pop('Tags')

            # Show the dialog
            dialog = InfoDialog(MainWindow(), info,
                                Application().layout.get_context_cue().name)
            dialog.exec_()


class InfoDialog(QDialog):
    def __init__(self, parent, info, title):
        super().__init__(parent)

        self.setWindowTitle(
            translate('MediaInfo', 'Media Info') + ' - ' + title)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setMinimumSize(550, 300)
        self.resize(550, 500)

        self.vLayout = QVBoxLayout(self)

        self.infoTree = QTreeWidget(self)
        self.infoTree.setColumnCount(2)
        self.infoTree.setHeaderLabels([translate('MediaInfo', 'Info'),
                                       translate('MediaInfo', 'Value')])
        self.infoTree.setAlternatingRowColors(True)
        self.infoTree.setSelectionMode(QAbstractItemView.NoSelection)
        self.infoTree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.infoTree.header().setStretchLastSection(False)
        self.infoTree.header().setSectionResizeMode(
            QHeaderView.ResizeToContents)
        self.vLayout.addWidget(self.infoTree)

        self.__generate_items(info)
        self.infoTree.expandAll()

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)
        self.vLayout.addWidget(self.buttonBox)

        self.buttonBox.rejected.connect(self.close)

    def __generate_items(self, info, parent=None):
        for key in sorted(info.keys()):
            if isinstance(info[key], dict):
                widget = QTreeWidgetItem([key])
                self.__generate_items(info[key], widget)
            else:
                widget = QTreeWidgetItem([key, info[key]])

            if parent is not None:
                parent.addChild(widget)
            else:
                self.infoTree.addTopLevelItem(widget)
