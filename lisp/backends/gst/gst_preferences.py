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

from PyQt5.QtWidgets import QVBoxLayout, QPushButton

from lisp.backends.gst.gst_pipe_edit import GstPipeEdit
from lisp.ui.settings.section import SettingsSection


class GstPreferences(SettingsSection):

    NAME = 'GStreamer settings'

    def __init__(self, size, parent=None):
        super().__init__(size, parent)

        self.setLayout(QVBoxLayout())

        self.editPipeline = QPushButton(self)
        self.editPipeline.setText('Change default pipeline')
        self.editPipeline.clicked.connect(self.show_dialog)
        self.layout().addWidget(self.editPipeline)
        self.layout().addSpacing(self.height() - 80)

    def show_dialog(self):
        edit = GstPipeEdit(self._pipe, preferences_mode=True)
        if edit.exec_() == edit.Accepted:
            self._pipe = edit.get_pipe()

    def get_configuration(self):
        return {'Gst': {'pipeline': self._pipe}}

    def set_configuration(self, conf):
        self._pipe = conf['Gst']['pipeline'].replace(' ', '')
