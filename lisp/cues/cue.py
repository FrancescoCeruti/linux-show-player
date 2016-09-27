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
from enum import Enum, IntEnum
from threading import Event
from uuid import uuid4

from lisp.core.decorators import async, synchronized_method
from lisp.core.has_properties import HasProperties, Property, WriteOnceProperty
from lisp.core.signal import Signal


class CueState(IntEnum):
    Error = -1
    Stop = 0
    Running = 1
    Pause = 2


class CueAction(Enum):
    Default = 'Default'
    Start = 'Start'
    Stop = 'Stop'
    Pause = 'Pause'


class CueNextAction(Enum):
    DoNothing = 'DoNothing'
    AutoNext = 'AutoNext'
    AutoFollow = 'AutoFollow'


# TODO: pause-able pre/post wait
class Cue(HasProperties):
    """Cue(s) are the base component for implement any kind of live-controllable
    element (live = during a show).

    A cue implement his behavior(s) reimplementing the __start__, __stop__ and
    __pause__ methods.
    Can be triggered calling the execute() method, providing the action to
    be executed, or calling directly start()/stop() or pause().

    .. note:
        If needed __start__, __stop__ and __pause__ can be asynchronous.

    Cue provide **(and any subclass should do the same)** properties via
    HasProperties/Property specifications.

    :ivar _type_: Cue type (class name). Should NEVER change after init.
    :ivar id: Identify the cue uniquely. Should NEVER change after init.
    :ivar index: Cue position in the view.
    :ivar name: Cue visualized name.
    :ivar description: Cue text description.
    :ivar stylesheet: Cue style, used by the view.
    :ivar duration: The cue duration in milliseconds. (0 means no duration)
    :ivar stop_pause: If True, by default the cue is paused instead of stopped.
    :ivar pre_wait: Cue pre-wait in seconds.
    :ivar post_wait: Cue post-wait in seconds (see note).
    :ivar next_action: What do after post_wait (see note).
    :cvar CueActions: actions supported by the cue (default: CueAction.Start)

    A cue should declare CueAction.Default as supported only if CueAction.Start
    and CueAction.Stop are both supported.

    .. Note::
        If 'next_action' is set to CueNextAction.AutoFollow value, then the
        'post_wait' value is ignored.

    """

    _type_ = WriteOnceProperty()
    id = WriteOnceProperty()
    name = Property(default='Untitled')
    index = Property(default=-1)
    description = Property(default='')
    stylesheet = Property(default='')
    duration = Property(default=0)
    stop_pause = Property(default=False)
    pre_wait = Property(default=0)
    post_wait = Property(default=0)
    next_action = Property(default=CueNextAction.DoNothing.value)

    CueActions = (CueAction.Start, )

    def __init__(self, id=None):
        super().__init__()
        self._waiting = Event()
        self._waiting.set()

        self.id = str(uuid4()) if id is None else id
        self._type_ = self.__class__.__name__

        self.pre_wait_enter = Signal()
        self.pre_wait_exit = Signal()       # True if not interrupted
        self.post_wait_enter = Signal()
        self.post_wait_exit = Signal()      # True if not interrupted

        self.started = Signal()     # self
        self.stopped = Signal()     # self
        self.paused = Signal()      # self
        self.error = Signal()       # self, error, details
        self.next = Signal()        # self
        self.end = Signal()         # self

        self.stopped.connect(self._waiting.set)
        self.changed('next_action').connect(self.__next_action_changed)

    def execute(self, action=CueAction.Default):
        """Execute the specified action, if supported.

        .. Note::
            Even if not specified in Cue.CueActions, when CueAction.Default
            is given, a "default" action is selected depending on the current
            cue state, if this action is not supported nothing will be done.

        :param action: the action to be performed
        """
        if action == CueAction.Default:
            if self.state == CueState.Running:
                if self.stop_pause and CueAction.Pause in self.CueActions:
                    action = CueAction.Pause
                else:
                    action = CueAction.Stop
            elif self.is_waiting():
                self._waiting.set()
                return
            else:
                action = CueAction.Start

        if action in self.CueActions:
            if action == CueAction.Start:
                self.start()
            elif action == CueAction.Stop:
                self.stop()
            elif action == CueAction.Pause:
                self.pause()

    @async
    @synchronized_method(blocking=True)
    def start(self):
        """Start the cue.

        .. note::
            Calling during pre/post wait has no effect.
        """

        do_wait = self.state == CueState.Stop or self.state == CueState.Error
        # The pre/post waits are done only if going from stop->start or
        # error->start.
        if do_wait and not self.__pre_wait():
            # self.__pre_wait() is executed only if do_wait is True
            # if self.__pre_wait() return False, the wait is been interrupted
            # so the cue doesn't start.
            return

        # Start the cue
        self.__start__()

        if do_wait and self.next_action != CueNextAction.AutoFollow.value:
            # If next-action is AutoFollow no post-wait is executed, in this
            # case higher-level components should watch directly the cue-state
            # signals.
            if self.__post_wait() and self.next_action == CueNextAction.AutoNext.value:
                # If the post-wait is not interrupted and the next-action
                # is AutoNext, than emit the 'next' signal.
                self.next.emit(self)

    @abstractmethod
    def __start__(self):
        pass

    def stop(self):
        """Stop the cue.

        .. note::
            If called during pre/post wait, the wait is interrupted.
        """
        self._waiting.set()  # Stop the wait
        self.__stop__()

    def __stop__(self):
        pass

    def pause(self):
        """Pause the cue.

        .. note::
            Calling during pre/post wait has no effect.
        """
        if not self.is_waiting():
            self.__pause__()

    def __pause__(self):
        pass

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
        return not self._waiting.is_set()

    def __pre_wait(self):
        """Return False if the wait is interrupted"""
        not_stopped = True
        if self.pre_wait > 0:
            self.pre_wait_enter.emit()
            self._waiting.clear()
            not_stopped = not self._waiting.wait(self.pre_wait)
            self._waiting.set()
            self.pre_wait_exit.emit(not_stopped)

        return not_stopped

    def __post_wait(self):
        """Return False if the wait is interrupted"""
        not_stopped = True
        if self.post_wait > 0:
            self.post_wait_enter.emit()
            self._waiting.clear()
            not_stopped = not self._waiting.wait(self.post_wait)
            self._waiting.set()
            self.post_wait_exit.emit(not_stopped)

        return not_stopped

    def __next_action_changed(self, next_action):
        self.end.disconnect(self.next.emit)
        if next_action == CueNextAction.AutoFollow.value:
            self.end.connect(self.next.emit)
