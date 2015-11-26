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

from abc import abstractmethod
from enum import Enum
from threading import Event
from uuid import uuid4

from lisp.core.decorators import async
from lisp.core.has_properties import HasProperties, Property
from lisp.core.signal import Signal


class CueState(Enum):
    Error = -1
    Stop = 0
    Running = 1
    Pause = 2


class CueNextAction(Enum):
    DoNothing = 'DoNothing'
    AutoNext = 'AutoNext'
    AutoFollow = 'AutoFollow'


class Cue(HasProperties):
    """Cue(s) are the base component for implement any kind of live-controllable
    element (live = during a show).

    A cue implement his behavior(s) in the __execute__() method, and can
    be triggered calling the execute() method. Any cue must provide the
    available "actions" via an class-member enumeration named "CueAction".

    .. note:
        The execute() implementation can ignore the specified action if
        some condition is not matched (e.g. trying to pause a stopped track).

    Cue provide **(and any subclass should do the same)** properties via
    HasProperties/Property specifications.

    :ivar _type_: Cue type (class name). Should NEVER change after init.
    :ivar id: Identify the cue uniquely. Should NEVER change after init.
    :ivar index: Cue position in the view.
    :ivar name: Cue visualized name.
    :ivar stylesheet: Cue style, used by the view.
    :ivar duration: The cue duration in milliseconds. (0 means no duration)
    :ivar pre_wait: Cue pre-wait in seconds.
    :ivar post_wait: Cue post-wait in seconds (see note).
    :ivar next_action: What do after post_wait (see note).

    .. Note::
        If 'next_action' is set to CueNextAction.AutoFollow value, then the
        'post_wait' value is ignored.

    """

    class CueAction(Enum):
        Default = 0
        Play = 1
        Pause = 2
        Stop = 3

    _type_ = Property()
    id = Property()
    index = Property(default=-1)
    name = Property(default='Untitled')
    stylesheet = Property(default='')
    duration = Property(default=0)
    pre_wait = Property(default=0)
    post_wait = Property(default=0)
    next_action = Property(default=CueNextAction.DoNothing.value)

    def __init__(self, id=None):
        super().__init__()
        self._wait_event = Event()
        self._wait_event.set()

        self.id = str(uuid4()) if id is None else id
        self._type_ = self.__class__.__name__

        self.pre_wait_enter = Signal()
        self.pre_wait_exit = Signal()
        self.post_wait_enter = Signal()
        self.post_wait_exit = Signal()

        self.start = Signal()
        self.pause = Signal()
        self.error = Signal()
        self.stop = Signal()
        self.end = Signal()
        self.next = Signal()

        self.stop.connect(self._wait_event.set)
        self.changed('next_action').connect(self.__next_action_changed)

    @async
    def execute(self, action=None):
        """Execute the cue. NOT thread safe

        :param action: the action to be performed
        """
        # TODO: Thread-safe (if needed)
        state = self.state
        if state == CueState.Stop or state == CueState.Error:
            if self.is_waiting():
                self.stop.emit(self)
                return

            if not self.__pre_wait():
                return

        if action is None:
            self.__execute__()
        else:
            self.__execute__(action)

        if state == CueState.Stop or state == CueState.Error:
            if self.next_action != CueNextAction.AutoFollow.value:
                if self.__post_wait() and self.next_action == CueNextAction.AutoNext.value:
                    self.next.emit(self)

    @abstractmethod
    def __execute__(self, action=CueAction.Default):
        """"""

    def current_time(self):
        """Return the current execution time if available, otherwise 0.

        :rtype: int
        """
        return 0

    @property
    @abstractmethod
    def state(self):
        """Return the current state.

        During pre/post-wait the cue is considered in Stop state.

        :rtype: CueState
        """

    def is_waiting(self):
        return not self._wait_event.is_set()

    def __pre_wait(self):
        """Return False if the wait is interrupted"""
        not_stopped = True
        if self.pre_wait > 0:
            self.pre_wait_enter.emit()
            self._wait_event.clear()
            not_stopped = not self._wait_event.wait(self.pre_wait)
            self._wait_event.set()
            self.pre_wait_exit.emit()

        return not_stopped

    def __post_wait(self):
        """Return False if the wait is interrupted"""
        not_stopped = True
        if self.post_wait > 0:
            self.post_wait_enter.emit()
            self._wait_event.clear()
            not_stopped = not self._wait_event.wait(self.post_wait)
            self._wait_event.set()
            self.post_wait_exit.emit()

        return not_stopped

    def __next_action_changed(self, next_action):
        self.end.disconnect(self.next.emit)
        if next_action == CueNextAction.AutoFollow.value:
            self.end.connect(self.next.emit)
