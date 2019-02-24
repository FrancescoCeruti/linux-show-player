# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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
from PyQt5.QtWidgets import (
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QTreeWidget,
    QAbstractItemView,
    QDialogButtonBox,
    QTreeWidgetItem,
    QHeaderView,
)

from lisp.core.plugin import Plugin
from lisp.cues.media_cue import MediaCue
from lisp.layout.cue_layout import CueLayout
from lisp.layout.cue_menu import (
    MenuActionsGroup,
    SimpleMenuAction,
    MENU_PRIORITY_PLUGIN,
)
from lisp.plugins.gst_backend.gst_utils import (
    gst_uri_metadata,
    gst_parse_tags_list,
)
from lisp.ui.ui_utils import translate


class MediaInfo(Plugin):

    Name = "Media-Cue information dialog"
    Authors = ("Francesco Ceruti",)
    Description = "Provide a function to show information on media-cues source"
    Depends = ("GstBackend",)

    def __init__(self, app):
        super().__init__(app)

        self.cue_action_group = MenuActionsGroup(priority=MENU_PRIORITY_PLUGIN)
        self.cue_action_group.add(
            SimpleMenuAction(
                translate("MediaInfo", "Media Info"), self._show_info
            )
        )

        CueLayout.CuesMenu.add(self.cue_action_group, MediaCue)

    def _show_info(self, cue):
        media_uri = cue.media.input_uri()

        if media_uri is None:
            QMessageBox.warning(
                self.app.window,
                translate("MediaInfo", "Warning"),
                translate("MediaInfo", "No info to display"),
            )
        else:
            if media_uri.startswith("file://"):
                media_uri = "file://" + self.app.session.abs_path(media_uri[7:])

            gst_info = gst_uri_metadata(media_uri)
            info = {"URI": unquote(gst_info.get_uri())}

            # Audio streams info
            for stream in gst_info.get_audio_streams():
                name = stream.get_stream_type_nick().capitalize()
                info[name] = {
                    "Bitrate": str(stream.get_bitrate() // 1000) + " Kb/s",
                    "Channels": str(stream.get_channels()),
                    "Sample rate": str(stream.get_sample_rate()) + " Hz",
                    "Sample size": str(stream.get_depth()) + " bit",
                }

            # Video streams info
            for stream in gst_info.get_video_streams():
                name = stream.get_stream_type_nick().capitalize()
                info[name] = {
                    "Height": str(stream.get_height()) + " px",
                    "Width": str(stream.get_width()) + " px",
                    "Framerate": str(
                        round(
                            stream.get_framerate_num()
                            / stream.get_framerate_denom()
                        )
                    ),
                }

            # Tags
            gst_tags = gst_info.get_tags()
            tags = {}

            if gst_tags is not None:
                for name, value in gst_parse_tags_list(gst_tags).items():
                    tag_txt = str(value)

                    # Include the value only if it's representation make sense
                    if tag_txt != object.__str__(value):
                        tags[name.capitalize()] = tag_txt

                if tags:
                    info["Tags"] = tags

            # Show the dialog
            dialog = InfoDialog(self.app.window, info, cue.name)
            dialog.exec()


class InfoDialog(QDialog):
    def __init__(self, parent, info, title):
        super().__init__(parent)

        self.setWindowTitle(
            translate("MediaInfo", "Media Info") + " - " + title
        )
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setMinimumSize(600, 300)
        self.resize(600, 300)
        self.setLayout(QVBoxLayout(self))

        self.infoTree = QTreeWidget(self)
        self.infoTree.setColumnCount(2)
        self.infoTree.setHeaderLabels(
            [translate("MediaInfo", "Info"), translate("MediaInfo", "Value")]
        )
        self.infoTree.setAlternatingRowColors(True)
        self.infoTree.setSelectionMode(QAbstractItemView.NoSelection)
        self.infoTree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.infoTree.header().setStretchLastSection(False)
        self.infoTree.header().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.layout().addWidget(self.infoTree)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)
        self.buttonBox.rejected.connect(self.close)
        self.layout().addWidget(self.buttonBox)

        self.populateTree(info)
        self.infoTree.expandAll()

    def populateTree(self, info, parent=None):
        for key in sorted(info.keys()):
            if isinstance(info[key], dict):
                widget = QTreeWidgetItem([key])
                self.populateTree(info[key], widget)
            else:
                widget = QTreeWidgetItem([key, info[key]])

            if parent is not None:
                parent.addChild(widget)
            else:
                self.infoTree.addTopLevelItem(widget)
