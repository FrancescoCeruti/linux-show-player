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

from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QWidget


class SettingsSection(QWidget):

    Name = 'Section'

    def __init__(self, size=QRect(), cue=None, parent=None):
        super().__init__(parent)
        self.resize(self.sizeHint() if size is None else size)

        self.cue = cue

    def enable_check(self, enable):
        ''' Enable option check '''

    def get_configuration(self):
        ''' Return the current settings '''
        return {}

    def set_configuration(self, conf):
        ''' Load the settings '''
