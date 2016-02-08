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

from PyQt5.QtWidgets import QTreeWidgetItem


class ActionItem(QTreeWidgetItem):

    def __init__(self, cue):
        super().__init__()

        self.selected = False
        self.cue = cue

        self.setText(1, cue.name)
        self.cue.changed('name').connect(self.update_item)

    def update_item(self):
        self.setText(1, self.cue.name)

    def select(self):
        self.selected = not self.selected
