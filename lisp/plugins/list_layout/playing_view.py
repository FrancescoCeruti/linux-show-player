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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from lisp.core.signal import Connection
from lisp.plugins.list_layout.playing_widgets import get_running_widget


class RunningCuesListWidget(QListWidget):
    def __init__(self, running_model, config, **kwargs):
        super().__init__(**kwargs)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionMode(self.NoSelection)

        self._config = config

        self._running_cues = {}
        self._running_model = running_model
        self._running_model.item_added.connect(
            self._item_added, Connection.QtQueued
        )
        self._running_model.item_removed.connect(
            self._item_removed, Connection.QtQueued
        )
        self._running_model.model_reset.connect(
            self._model_reset, Connection.QtQueued
        )

        self.__dbmeter_visible = False
        self.__seek_visible = False
        self.__accurate_time = False

    @property
    def dbmeter_visible(self):
        return self.__dbmeter_visible

    @dbmeter_visible.setter
    def dbmeter_visible(self, visible):
        self.__dbmeter_visible = visible
        for item in self._running_cues.values():
            try:
                self.itemWidget(item).set_dbmeter_visible(visible)
            except AttributeError:
                pass

    @property
    def seek_visible(self):
        return self.__seek_visible

    @seek_visible.setter
    def seek_visible(self, visible):
        self.__seek_visible = visible
        for item in self._running_cues.values():
            try:
                self.itemWidget(item).set_seek_visible(visible)
            except AttributeError:
                pass

    @property
    def accurate_time(self):
        return self.__accurate_time

    @accurate_time.setter
    def accurate_time(self, accurate):
        self.__accurate_time = accurate
        for item in self._running_cues.values():
            self.itemWidget(item).set_accurate_time(accurate)

    def _item_added(self, cue):
        widget = get_running_widget(cue, self._config, parent=self)
        widget.set_accurate_time(self.__accurate_time)
        try:
            widget.set_dbmeter_visible(self.__dbmeter_visible)
            widget.set_seek_visible(self.__seek_visible)
        except AttributeError:
            pass

        item = QListWidgetItem()
        item.setSizeHint(widget.size())

        self.addItem(item)
        self.setItemWidget(item, widget)
        self._running_cues[cue] = item

    def _item_removed(self, cue):
        item = self._running_cues.pop(cue)
        widget = self.itemWidget(item)
        row = self.indexFromItem(item).row()

        self.removeItemWidget(item)
        self.takeItem(row)

        widget.deleteLater()

    def _model_reset(self):
        for cue in list(self._running_cues.keys()):
            self._item_removed(cue)
