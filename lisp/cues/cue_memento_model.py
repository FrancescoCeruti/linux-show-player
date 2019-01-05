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

from lisp.core.memento_model import MementoModelAdapter
from lisp.core.memento_model_actions import (
    AddItemAction,
    MoveItemAction,
    RemoveItemAction,
)


class CueMementoAdapter(MementoModelAdapter):
    def __init__(self, model_adapter, handler=None):
        super().__init__(model_adapter, handler)
        self._add_action = CueAddAction
        self._remove_action = CueRemoveAction
        self._move_action = CueMoveAction


# TODO: keep only the cue-properties for the cue-removed/added action ??


class CueAddAction(AddItemAction):
    def log(self):
        return 'Add cue "{}"'.format(self._item.name)


class CueRemoveAction(RemoveItemAction):
    def log(self):
        return 'Remove cue "{}"'.format(self._item.name)


class CueMoveAction(MoveItemAction):
    def log(self):
        return 'Move cue from "{}" to "{}"'.format(
            self._old_index + 1, self._new_index + 1
        )
