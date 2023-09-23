# This file is part of Linux Show Player
#
# Copyright 2019 Francesco Ceruti <ceppofrancy@gmail.com>
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

from .command import Command


class ModelCommand(Command):
    __slots__ = "_model"

    def __init__(self, model):
        self._model = model


class ModelItemsCommand(ModelCommand):
    __slots__ = "_items"

    def __init__(self, model, *items):
        super().__init__(model)
        self._items = items


class ModelAddItemsCommand(ModelItemsCommand):
    def __init__(self, model, *items):
        super().__init__(model, *items)

    def do(self):
        for item in self._items:
            self._model.add(item)

    def undo(self):
        for item in self._items:
            self._model.remove(item)


class ModelRemoveItemsCommand(ModelItemsCommand):
    def __init__(self, model, *items):
        super().__init__(model, *items)

    def do(self):
        for item in self._items:
            self._model.remove(item)

    def undo(self):
        for item in self._items:
            self._model.add(item)


class ModelInsertItemsCommand(ModelItemsCommand):
    __slots__ = ("_index",)

    def __init__(self, model_adapter, index, *items):
        super().__init__(model_adapter)
        self._index = index
        self._items = items

    def do(self):
        if self._index >= 0:
            # We know where we should insert the items
            for index, item in enumerate(self._items, self._index):
                self._model.insert(item, index)
        else:
            # We don't know where to insert the item, the model will choose the
            # best position
            for item in self._items:
                self._model.insert(item, -1)

    def undo(self):
        for item in self._items:
            self._model.remove(item)


class ModelMoveItemCommand(ModelCommand):
    __slots__ = ("_old_index", "_new_index")

    def __init__(self, model_adapter, old_index, new_index):
        super().__init__(model_adapter)
        self._old_index = old_index
        self._new_index = new_index

    def do(self):
        self._model.move(self._old_index, self._new_index)

    def undo(self):
        self._model.move(self._new_index, self._old_index)


class ModelMoveItemsCommand(ModelCommand):
    __slots__ = ("_old_indexes", "_new_index", "_before", "_after")

    def __init__(self, model_adapter, old_indexes, new_index):
        super().__init__(model_adapter)
        self._old_indexes = old_indexes
        self._new_index = new_index
        self._before = 0
        self._after = 0

        if self._new_index < 0:
            self._new_index = 0
        elif self._new_index >= len(model_adapter):
            self._new_index = len(model_adapter) - 1

        for old_index in old_indexes:
            if old_index < new_index:
                self._before += 1
            elif old_index > new_index:
                self._after += 1

    def do(self):
        before = after = 0
        shift = bool(self._before)

        for index in self._old_indexes:
            if index <= self._new_index:
                self._model.move(index - before, self._new_index)
                before += 1
            elif index > self._new_index:
                self._model.move(index, self._new_index + after + shift)
                after += 1

    def undo(self):
        before = self._before
        after = self._after
        shift = bool(self._before)

        for old_index in self._old_indexes:
            if old_index <= self._new_index:
                before -= 1
                self._model.move(self._new_index - before, old_index)
            elif old_index > self._new_index:
                after -= 1
                self._model.move(self._new_index + shift, old_index + after)
