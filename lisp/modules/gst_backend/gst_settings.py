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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox

from lisp.modules.gst_backend.gst_pipe_edit import GstPipeEdit
from lisp.ui.settings.settings_page import SettingsPage
from lisp.ui.ui_utils import translate


class GstSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'GStreamer settings')

    def __init__(self, **kwargs):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.pipeGroup = QGroupBox(self)
        self.pipeGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.pipeGroup)

        self.pipeEdit = GstPipeEdit([], app_mode=True)
        self.pipeGroup.layout().addWidget(self.pipeEdit)

        self.retranslateUi()

    def retranslateUi(self):
        self.pipeGroup.setTitle(translate('GstSettings', 'Pipeline'))

    def get_settings(self):
        return {'Gst': {'pipeline': ', '.join(self.pipeEdit.get_pipe())}}

    def load_settings(self, settings):
        pipe = tuple(settings['Gst']['pipeline'].replace(' ', '').split(','))
        self.pipeEdit.set_pipe(pipe)
