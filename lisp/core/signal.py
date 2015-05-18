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

from enum import Enum
import inspect
import traceback
import weakref
from types import MethodType

from PyQt5.QtCore import QEvent, QObject
from PyQt5.QtWidgets import QApplication

from lisp.core.decorators import synchronized, async


__all__ = ['Signal', 'Connection']


# TODO: check for memory leaks
class Slot:
    """Synchronous slot."""

    def __init__(self, slot, callback=None):
        if isinstance(slot, MethodType):
            self._reference = weakref.WeakMethod(slot, self._expired)
            self._no_args = len(inspect.getfullargspec(slot).args) == 1
        elif callable(slot):
            self._reference = weakref.ref(slot, self._expired)
            self._no_args = len(inspect.getfullargspec(slot).args) == 0
        else:
            raise TypeError('slot must be callable')

        self._callback = callback
        self._slot_id = id(slot)

    def call(self, *args, **kwargs):
        """Call the callable object within the given parameters."""
        if self.is_alive():
            if self._no_args:
                self._reference()()
            else:
                self._reference()(*args, **kwargs)

    def is_alive(self):
        return self._reference() is not None

    def _expired(self, reference):
        self._callback(self._slot_id)


class AsyncSlot(Slot):
    """Asynchronous slot."""

    @async
    def call(self, *args, **kwargs):
        super().call(*args, **kwargs)


class QtSlot(Slot):
    """Qt-safe synchronous slot, execute the call inside the qt-event-loop."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create a QObject and move it to mainloop thread
        self._invoker = QObject()
        self._invoker.moveToThread(QApplication.instance().thread())
        self._invoker.customEvent = self._custom_event

    def call(self, *args, **kwargs):
        QApplication.instance().sendEvent(self._invoker,
                                          self._event(*args, **kwargs))

    def _event(self, *args, **kwargs):
        return QSlotEvent(self._reference, *args, **kwargs)

    def _custom_event(self, event):
        super().call(*event.args, **event.kwargs)


class QtQueuedSlot(QtSlot):
    """Qt-safe asynchronous slot, execute the call inside the qt-event-loop."""

    def call(self, *args, **kwargs):
        QApplication.postEvent(self._invoker, self._event(*args, **kwargs))


class QSlotEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, reference, *args, **kwargs):
        QEvent.__init__(self, QSlotEvent.EVENT_TYPE)
        self.reference = reference
        self.args = args
        self.kwargs = kwargs


class Connection(Enum):
    """Available connection modes."""
    Direct = Slot
    Async = AsyncSlot
    QtDirect = QtSlot
    QtQueued = QtQueuedSlot

    def new_slot(self, slot, callback=None):
        return self.value(slot, callback)


class Signal:
    """Quite simple (qt-compatible) signal/slot implementation.

    A signal object can be connected/disconnected to a callable object (slot),
    the connection can have different modes, any mode define the way a slot
    is called, those are defined in :class:`ConnectionMode`.

    .. note::
        * Any object can be connected only once to a specific signal,
          if reconnected, the previous connection is overridden.
        * Internally weak-references are used, so disconnection is not needed
          before delete objects.
        * Signals with "arguments" can be connected to slot without arguments

    .. warning::
        Because of weakrefs connecting like the following can't work:

        signal.connect(lambda: print('Hello')))
        signal.connect(MyObject().my_method)
        signal.connect(something_not_referenced)
    """

    def __init__(self):
        self.__slots = {}

    def connect(self, slot, mode=Connection.Direct):
        """Connect the given slot, if not already connected.

        :param slot: The slot to be connected
        :param mode: Connection mode
        :type mode: Connection
        :raise ValueError: if mode not in ConnectionMode enum
        """
        if mode not in Connection:
            raise ValueError('invalid mode value: {0}'.format(mode))

        # Create a new Slot object, and use the object id as a key
        self.__slots[id(slot)] = mode.new_slot(slot, self._remove_slot)

    def disconnect(self, slot=None):
        """Disconnect the given slot, or all the slots if no slot is given.

        :param slot: The slot to be disconnected
        """
        if slot is not None:
            self._remove_slot(id(slot))
        else:
            self.__slots.clear()

    @synchronized
    def emit(self, *args, **kwargs):
        """Emit the signal within the given arguments"""
        for slot in self.__slots.values():
            try:
                slot.call(*args, **kwargs)
            except Exception:
                # TODO: Here we want the function reference in the stack
                traceback.print_exc()

    def _remove_slot(self, slot_id):
        self.__slots.pop(slot_id, None)
