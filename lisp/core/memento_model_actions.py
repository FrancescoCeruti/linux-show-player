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

from abc import abstractmethod

from lisp.core.action import Action


class MementoAction(Action):
    """Actions created by the MementoModel to register model changes."""

    __slots__ = ("_m_model", "_model")

    def __init__(self, m_model, model):
        super().__init__()
        self._m_model = m_model
        self._model = model

    def do(self):
        pass

    def undo(self):
        with self._m_model.lock():
            self.__undo__()

    def redo(self):
        with self._m_model.lock():
            self.__redo__()

    @abstractmethod
    def __undo__(self):
        pass

    @abstractmethod
    def __redo__(self):
        pass


class AddItemAction(MementoAction):

    __slots__ = "_item"

    def __init__(self, m_model, model, item):
        super().__init__(m_model, model)
        self._item = item

    def __undo__(self):
        self._model.remove(self._item)

    def __redo__(self):
        self._model.add(self._item)


class RemoveItemAction(MementoAction):

    __slots__ = "_item"

    def __init__(self, m_model, model, item):
        super().__init__(m_model, model)
        self._item = item

    def __undo__(self):
        self._model.add(self._item)

    def __redo__(self):
        self._model.remove(self._item)


class MoveItemAction(MementoAction):

    __slots__ = ("_old_index", "_new_index")

    def __init__(self, m_model, model_adapter, old_index, new_index):
        super().__init__(m_model, model_adapter)
        self._old_index = old_index
        self._new_index = new_index

    def __undo__(self):
        self._model.move(self._new_index, self._old_index)

    def __redo__(self):
        self._model.move(self._old_index, self._new_index)
