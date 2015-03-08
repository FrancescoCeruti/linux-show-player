##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from urllib.request import unquote

from PyQt5 import QtCore
from PyQt5.QtWidgets import QAction, QMessageBox, QDialog, QVBoxLayout, \
    QTreeWidget, QAbstractItemView, QDialogButtonBox, QTreeWidgetItem
from lisp.core.plugin import Plugin
from lisp.utils.audio_utils import uri_metadata, parse_gst_tag_list

from lisp.application import Application
from lisp.cues.media_cue import MediaCue


class MediaInfo(Plugin):

    Name = 'MediaInfo'

    def __init__(self):
        self.app = Application()

        self.actionMediaInfo = QAction(None, triggered=self.showInfo)
        self.actionMediaInfo.setText("Media Info")

        self.separator = self.app.layout.add_context_separator(MediaCue)
        self.app.layout.add_context_item(self.actionMediaInfo, MediaCue)

    def reset(self):
        self.app.layout.remove_context_item(self.actionMediaInfo)
        self.app.layout.remove_context_item(self.separator)

    def showInfo(self, clicked):
        media_uri = self.app.layout.get_context_cue().media.input_uri()
        if not media_uri:
            QMessageBox.critical(None, 'Error Message', 'Invalid Media!')
        else:
            gst_info = uri_metadata(media_uri)
            info = {"Uri": unquote(gst_info.get_uri())}

            # Audio streams info
            for stream in gst_info.get_audio_streams():
                name = stream.get_stream_type_nick().capitalize()
                info[name] = {"Bitrate": str(stream.get_bitrate() // 1000) +
                              " Kb/s",
                              "Channels": str(stream.get_channels()),
                              "Sample rate": str(stream.get_sample_rate()) +
                              " Hz",
                              "Sample size": str(stream.get_depth()) + " bit"
                              }

            # Video streams info
            for stream in gst_info.get_video_streams():
                name = stream.get_stream_type_nick().capitalize()
                framerate = round(stream.get_framerate_num() /
                                  stream.get_framerate_denom())
                info[name] = {"Height": str(stream.get_height()) + " px",
                              "Width": str(stream.get_width()) + " px",
                              "Framerate": str(framerate)
                              }

            # Media tags
            info["Tags"] = {}
            tags = parse_gst_tag_list(gst_info.get_tags())
            for tag_name in tags:
                if(not str(tags[tag_name]).startswith("<Gst")):
                    info["Tags"][tag_name.capitalize()] = str(tags[tag_name])

            if len(info["Tags"]) == 0:
                info.pop("Tags")

            # Show the dialog
            dialog = InfoDialog(self.app.mainWindow, info,
                                self.app.layout.get_context_cue()['name'])
            dialog.exec_()


class InfoDialog(QDialog):

    def __init__(self, parent, info, title):
        super().__init__(parent)

        self.setWindowTitle('Media Info - ' + title)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setMinimumSize(500, 250)
        self.resize(500, 250)

        self.vLayout = QVBoxLayout(self)

        self.infoTree = QTreeWidget(self)
        self.infoTree.setColumnCount(2)
        self.infoTree.setHeaderLabels(['Scope', 'Value'])
        self.infoTree.setAlternatingRowColors(True)
        self.infoTree.setSelectionMode(QAbstractItemView.NoSelection)
        self.infoTree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.vLayout.addWidget(self.infoTree)

        self.__generate_widgets(info)
        self.infoTree.setColumnWidth(0, 150)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)
        self.vLayout.addWidget(self.buttonBox)

        self.buttonBox.rejected.connect(self.close)

    def __generate_widgets(self, info, parent=None):
        for key in sorted(info.keys()):
            if(isinstance(info[key], dict)):
                widget = QTreeWidgetItem([key])
                self.__generate_widgets(info[key], widget)
            else:
                widget = QTreeWidgetItem([key, info[key]])

            if(parent):
                parent.addChild(widget)
            else:
                self.infoTree.addTopLevelItem(widget)
