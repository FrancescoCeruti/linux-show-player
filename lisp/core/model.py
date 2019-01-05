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
from collections.abc import Sized, Iterable, Container

from lisp.core.signal import Signal


class Model(Sized, Iterable, Container):
    """A model is a data container that provide signal to observe changes.

    The base model do not provide a way to change directly the data,
    this to remove useless restrictions to models that will store complex
    objects where attribute changes but not objects directly.
    Setter methods and signals can be simply implemented in subclass, where
    needed.

    A model should be as generic as possible in the way its store data, working
    like a normal data structure, for more ui-oriented tasks a ModelAdapter
    should be used.

    __iter__ must provide an iterator over the items
    __len__ must return the number of stored items
    __contains__ must return True/False if the given item is in/not in the model
    """

    def __init__(self):
        self.item_added = Signal()
        self.item_removed = Signal()
        self.model_reset = Signal()

    @abstractmethod
    def add(self, item):
        pass

    @abstractmethod
    def remove(self, item):
        pass

    @abstractmethod
    def reset(self):
        pass


class ModelException(Exception):
    """Exception for illegal operations on models"""
