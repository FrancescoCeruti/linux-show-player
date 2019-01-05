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

from lisp.core.proxy_model import ProxyModel
from lisp.core.signal import Signal


class ModelAdapter(ProxyModel):
    """Base-class for mutable ProxyModel(s) with index-based operations"""

    def __init__(self, model):
        super().__init__(model)
        self.item_moved = Signal()

    @abstractmethod
    def insert(self, item, index):
        pass

    @abstractmethod
    def item(self, index):
        pass

    @abstractmethod
    def pop(self, index):
        pass

    @abstractmethod
    def move(self, old_index, new_index):
        pass
