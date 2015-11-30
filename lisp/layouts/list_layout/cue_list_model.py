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

from lisp.core.model_adapter import ModelAdapter
from lisp.core.proxy_model import ReadOnlyProxyModel
from lisp.core.signal import Connection
from lisp.cues.media_cue import MediaCue


class CueListModel(ModelAdapter):

    def __init__(self, model):
        super().__init__(model)
        self.__cues = []

    def item(self, index):
        return self.__cues[index]

    def insert(self, item, index):
        item.index = index
        self.add(item)

    def pop(self, index):
        cue = self.__cues[index]
        self.model.remove(cue)
        return cue

    def move(self, old_index, new_index):
        if old_index != new_index:
            cue = self.__cues.pop(old_index)
            self.__cues.insert(new_index, cue)

            if old_index < new_index:
                min_index = old_index
                max_index = new_index
            else:
                min_index = new_index
                max_index = old_index

            self._update_indices(min_index, max_index + 1)
            self.item_moved.emit(old_index, new_index)

    def _model_reset(self):
        self.__cues.clear()
        self.model_reset.emit()

    def _item_added(self, item):
        if not isinstance(item.index, int) or not 0 <= item.index <= len(self.__cues):
            item.index = len(self.__cues)

        self.__cues.insert(item.index, item)
        self._update_indices(item.index)

        self.item_added.emit(item)

    def _item_removed(self, item):
        self.__cues.pop(item.index)
        self._update_indices(item.index)

        self.item_removed.emit(item)

    def _update_indices(self, start, stop=-1):
        """Update the indices of cues from start to stop-1"""
        if not 0 <= stop <= len(self.__cues):
            stop = len(self.__cues)

        for index in range(start, stop):
            self.__cues[index].index = index

    def __iter__(self):
        return self.__cues.__iter__()


class PlayingMediaCueModel(ReadOnlyProxyModel):

    def __init__(self, model):
        super().__init__(model)
        self.__cues = {}
        self.__playing = []

    def _item_added(self, item):
        if isinstance(item, MediaCue):
            self.__cues[item.media] = item

            item.media.on_play.connect(self._add, Connection.QtQueued)
            item.media.stopped.connect(self._remove, Connection.QtQueued)
            item.media.eos.connect(self._remove, Connection.QtQueued)
            item.media.interrupted.connect(self._remove, Connection.QtQueued)

    def _item_removed(self, item):
        if isinstance(item, MediaCue):
            item.media.on_play.disconnect(self._add)
            item.media.stopped.disconnect(self._remove)
            item.media.eos.disconnect(self._remove)
            item.media.interrupted.disconnect(self._remove)

            if item.media in self.__playing:
                self._remove(item.media)

            self.__cues.pop(item.media)

    def _model_reset(self):
        for cue in self.__cues:
            self._item_removed(cue)

        self.model_reset.emit()

    def _add(self, media):
        if media not in self.__playing:
            self.__playing.append(media)
            self.item_added.emit(self.__cues[media])

    def _remove(self, media):
        self.__playing.remove(media)
        self.item_removed.emit(self.__cues[media])

    def __len__(self):
        return len(self.__playing)

    def __iter__(self):
        for media in self.__playing:
            yield self.__cues[media]

    def __contains__(self, item):
        if isinstance(item, MediaCue):
            return item.media in self.__cues

        return False
