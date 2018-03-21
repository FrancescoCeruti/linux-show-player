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

from lisp.plugins.gst_backend.gst_pipe_edit import GstPipeEdit
from lisp.ui.settings.settings_page import ConfigurationPage
from lisp.ui.ui_utils import translate


class GstSettings(ConfigurationPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'GStreamer')

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.pipeGroup = QGroupBox(self)
        self.pipeGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.pipeGroup)

        self.pipeEdit = GstPipeEdit(config.get('pipeline'), app_mode=True)
        self.pipeGroup.layout().addWidget(self.pipeEdit)

        self.retranslateUi()

    def retranslateUi(self):
        self.pipeGroup.setTitle(translate('GstSettings', 'Pipeline'))

    def applySettings(self):
        self.config['pipeline'] = list(self.pipeEdit.get_pipe())
        self.config.write()