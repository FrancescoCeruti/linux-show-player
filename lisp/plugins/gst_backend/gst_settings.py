# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QLabel

from lisp.plugins.gst_backend.gst_pipe_edit import GstPipeEdit
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class GstSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "GStreamer")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.pipeGroup = QGroupBox(self)
        self.pipeGroup.setLayout(QVBoxLayout())
        self.pipeGroup.layout().setSpacing(
            self.pipeGroup.layout().contentsMargins().top()
        )
        self.layout().addWidget(self.pipeGroup)

        self.noticeLabel = QLabel(self.pipeGroup)
        self.noticeLabel.setAlignment(Qt.AlignCenter)
        font = self.noticeLabel.font()
        font.setPointSizeF(font.pointSizeF() * 0.9)
        self.noticeLabel.setFont(font)
        self.pipeGroup.layout().addWidget(self.noticeLabel)

        self.pipeEdit = GstPipeEdit("", app_mode=True)
        self.pipeGroup.layout().addWidget(self.pipeEdit)

        self.retranslateUi()

    def retranslateUi(self):
        self.pipeGroup.setTitle(translate("GstSettings", "Default pipeline"))
        self.noticeLabel.setText(
            translate("GstSettings", "Applied only to new cues.")
        )

    def loadSettings(self, settings):
        self.pipeEdit.set_pipe(settings["pipeline"])

    def getSettings(self):
        return {"pipeline": list(self.pipeEdit.get_pipe())}
