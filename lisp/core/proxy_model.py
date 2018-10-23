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

from abc import abstractmethod

from lisp.core.model import Model, ModelException


class ABCProxyModel(Model):
    def __init__(self, model):
        super().__init__()

        if not isinstance(model, Model):
            raise TypeError(
                "ProxyModel model must be a Model object, not {0}".format(
                    typename(model)
                )
            )

        self._model = model
        self._model.item_added.connect(self._item_added)
        self._model.item_removed.connect(self._item_removed)
        self._model.model_reset.connect(self._model_reset)

    @property
    def model(self):
        return self._model

    @abstractmethod
    def _model_reset(self):
        pass

    @abstractmethod
    def _item_added(self, item):
        pass

    @abstractmethod
    def _item_removed(self, item):
        pass


class ProxyModel(ABCProxyModel):
    """Proxy that wrap a more generic model to extend its functionality.

    The add, remove, __iter__, __len__ and __contains__ default implementations
    use the the model ones.

    .. note:
        The base model cannot be changed.
        Any ProxyModel could provide it's own methods/signals.
    """

    def add(self, item):
        self._model.add(item)

    def remove(self, item):
        self._model.remove(item)

    def reset(self):
        self._model.reset()

    def __iter__(self):
        return self._model.__iter__()

    def __len__(self):
        return len(self._model)

    def __contains__(self, item):
        return item in self._model


class ReadOnlyProxyModel(ProxyModel):
    def add(self, item):
        raise ModelException("cannot add items into a read-only model")

    def remove(self, item):
        raise ModelException("cannot remove items from a read-only model")

    def reset(self):
        raise ModelException("cannot reset read-only model")
