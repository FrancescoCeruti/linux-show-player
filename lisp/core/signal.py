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

import inspect
import logging
import traceback
import weakref
from enum import Enum
from threading import RLock
from types import MethodType, BuiltinMethodType

from PyQt5.QtCore import QEvent, QObject
from PyQt5.QtWidgets import QApplication

from lisp.core.decorators import async_function
from lisp.core.util import weak_call_proxy

__all__ = ["Signal", "Connection"]

logger = logging.getLogger(__name__)


def slot_id(slot_callable):
    """Return the id of the given slot_callable.

    This function is able to produce unique id(s) even for bounded methods, and
    builtin-methods using a combination of the function id and the object id.
    """
    if isinstance(slot_callable, MethodType):
        return id(slot_callable.__func__), id(slot_callable.__self__)
    elif isinstance(slot_callable, BuiltinMethodType):
        return id(slot_callable), id(slot_callable.__self__)
    else:
        return id(slot_callable)


class Slot:
    """Synchronous slot."""

    def __init__(self, slot_callable, callback=None):
        if isinstance(slot_callable, MethodType):
            self._reference = weakref.WeakMethod(slot_callable, self._expired)
        elif callable(slot_callable):
            self._reference = weakref.ref(slot_callable, self._expired)
        else:
            raise TypeError("slot must be callable")

        self._callback = callback
        self._slot_id = slot_id(slot_callable)
        self._no_args = len(inspect.signature(slot_callable).parameters) == 0

    def call(self, *args, **kwargs):
        """Call the callable object within the given parameters."""
        try:
            if self.is_alive():
                if self._no_args:
                    self._reference()()
                else:
                    self._reference()(*args, **kwargs)
        except Exception as e:
            logger.warning(str(e), exc_info=True)

    def is_alive(self):
        return self._reference() is not None

    def _expired(self, reference):
        self._callback(self._slot_id)


class AsyncSlot(Slot):
    """Asynchronous slot, NOT queued, any call is performed in a new thread."""

    @async_function
    def call(self, *args, **kwargs):
        super().call(*args, **kwargs)


class QtSlot(Slot):
    """Qt direct slot, execute the call inside the qt-event-loop."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create a QObject and move it to mainloop thread
        self._invoker = QObject()
        self._invoker.moveToThread(QApplication.instance().thread())
        self._invoker.customEvent = self._custom_event

    def call(self, *args, **kwargs):
        QApplication.instance().sendEvent(
            self._invoker, self._event(*args, **kwargs)
        )

    def _event(self, *args, **kwargs):
        return QSlotEvent(self._reference, *args, **kwargs)

    def _custom_event(self, event):
        super().call(*event.args, **event.kwargs)


class QtQueuedSlot(QtSlot):
    """Qt queued (safe) slot, execute the call inside the qt-event-loop."""

    def call(self, *args, **kwargs):
        QApplication.instance().postEvent(
            self._invoker, self._event(*args, **kwargs)
        )


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

    def new_slot(self, slot_callable, callback=None):
        return self.value(slot_callable, callback)


class Signal:
    """Signal/slot implementation.

    A signal object can be connected/disconnected to a callable object (slot),
    the connection can have different modes, any mode define the way a slot
    is called, those are defined in :class:`Connection`.

    .. note::
        * Any slot can be connected only once to a specific signal,
          if reconnected, the previous connection is overridden.
        * Internally, weak-references are used, so disconnection is not needed
          before delete a slot-owner object.
        * Signals with "arguments" can be connected to slot without arguments

    .. warning::
        Because of weakrefs, connecting like the following can't work:

        signal.connect(lambda: some_operation))
        signal.connect(NewObject().my_method)
        signal.connect(something_not_referenced)
    """

    def __init__(self):
        self.__slots = {}
        self.__lock = RLock()

    def connect(self, slot_callable, mode=Connection.Direct):
        """Connect the given slot, if not already connected.

        :param slot_callable: The slot (a python callable) to be connected
        :param mode: Connection mode
        :type mode: Connection
        :raise ValueError: if mode not in Connection enum
        """
        if mode not in Connection:
            raise ValueError("invalid mode value: {0}".format(mode))

        with self.__lock:
            sid = slot_id(slot_callable)
            # If already connected do nothing
            if sid not in self.__slots:
                # Create a new Slot object, use a weakref for the callback
                # to avoid cyclic references.
                self.__slots[sid] = mode.new_slot(
                    slot_callable,
                    weak_call_proxy(weakref.WeakMethod(self.__remove_slot)),
                )

    def disconnect(self, slot=None):
        """Disconnect the given slot, or all if no slot is specified.

        :param slot: The slot to be disconnected or None
        """
        if slot is not None:
            self.__remove_slot(slot_id(slot))
        else:
            with self.__lock:
                self.__slots.clear()

    def emit(self, *args, **kwargs):
        """Emit the signal within the given arguments"""
        with self.__lock:
            for slot in self.__slots.values():
                try:
                    slot.call(*args, **kwargs)
                except Exception:
                    traceback.print_exc()

    def __remove_slot(self, id_):
        with self.__lock:
            self.__slots.pop(id_, None)
