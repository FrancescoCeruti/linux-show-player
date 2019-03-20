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

from threading import Lock
from uuid import uuid4

from lisp.core.configuration import AppConfig
from lisp.core.decorators import async_function
from lisp.core.fade_functions import FadeInType, FadeOutType
from lisp.core.has_properties import HasProperties
from lisp.core.properties import Property, WriteOnceProperty
from lisp.core.rwait import RWait
from lisp.core.signal import Signal
from lisp.core.util import EqEnum, typename


class CueState:
    Invalid = 0

    Error = 1
    Stop = 2
    Running = 4
    Pause = 8

    PreWait = 16
    PostWait = 32
    PreWait_Pause = 64
    PostWait_Pause = 128

    IsRunning = Running | PreWait | PostWait
    IsPaused = Pause | PreWait_Pause | PostWait_Pause
    IsStopped = Error | Stop


class CueAction(EqEnum):
    Default = "Default"
    FadeIn = "FadeIn"
    FadeOut = "FadeOut"
    FadeInStart = "FadeInStart"
    FadeInResume = "FadeInResume"
    FadeOutPause = "FadeOutPause"
    FadeOutStop = "FadeOutStop"
    FadeOutInterrupt = "FadeOutInterrupt"
    Interrupt = "Interrupt"
    Start = "Start"
    Resume = "Resume"
    Pause = "Pause"
    Stop = "Stop"
    DoNothing = "DoNothing"


class CueNextAction(EqEnum):
    DoNothing = "DoNothing"
    TriggerAfterWait = "TriggerAfterWait"
    TriggerAfterEnd = "TriggerAfterEnd"
    SelectAfterWait = "SelectAfterWait"
    SelectAfterEnd = "SelectAfterEnd"


class Cue(HasProperties):
    """Cue(s) are the base component for implement any kind of live-controllable
    element (live = during a show).

    A cue implement his behavior(s) reimplementing __start__, __stop__,
    __pause__ and __interrupt__ methods.

    Cue provide **(and any subclass should do the same)** properties via
    HasProperties/Property specifications.

    :ivar _type_: Cue type (class name). Should NEVER change after init.
    :ivar id: Identify the cue uniquely. Should NEVER change after init.
    :ivar index: Cue position in the view.
    :ivar name: Cue visualized name.
    :ivar description: Cue text description.
    :ivar stylesheet: Cue style, used by the view.
    :ivar duration: The cue duration in milliseconds. (0 means no duration)
    :ivar pre_wait: Cue pre-wait in seconds.
    :ivar post_wait: Cue post-wait in seconds.
    :ivar next_action: What do after post_wait.
    :ivar fadein_type: Fade-In type
    :ivar fadeout_type: Fade-Out type
    :ivar fadein_duration: Fade-In duration in seconds
    :ivar fadeout_duration: Fade-Out duration in seconds
    :ivar default_start_action: action to execute to start
    :ivar default_stop_action: action to execute to stop
    :cvar CueActions: actions supported by the cue (default: CueAction.Start)

    A cue should declare CueAction.Default as supported only if CueAction.Start
    and CueAction.Stop are both supported.
    If CueAction.Stop is supported, CueAction.Interrupt should be supported.
    CueAction.DoNothing doesn't need to be declared, it should always be
    considered as supported.

    .. Note::
        If 'next_action' is AutoFollow or DoNothing, the postwait is not
        performed.
    """

    Name = "Cue"

    _type_ = WriteOnceProperty()
    id = WriteOnceProperty()
    name = Property(default="Untitled")
    index = Property(default=-1)
    description = Property(default="")
    stylesheet = Property(default="")
    duration = Property(default=0)
    pre_wait = Property(default=0)
    post_wait = Property(default=0)
    next_action = Property(default=CueNextAction.DoNothing.value)
    fadein_type = Property(default=FadeInType.Linear.name)
    fadeout_type = Property(default=FadeOutType.Linear.name)
    fadein_duration = Property(default=0)
    fadeout_duration = Property(default=0)
    default_start_action = Property(default=CueAction.Start.value)
    default_stop_action = Property(default=CueAction.Stop.value)

    CueActions = (CueAction.Start,)

    def __init__(self, id=None):
        super().__init__()
        self.id = str(uuid4()) if id is None else id
        self._type_ = typename(self)

        self._st_lock = Lock()
        self._state = CueState.Stop
        self._prewait = RWait()
        self._postwait = RWait()

        # Pre-Wait signals
        self.prewait_start = self._prewait.start
        self.prewait_ended = self._prewait.ended
        self.prewait_paused = self._prewait.paused
        self.prewait_stopped = self._prewait.stopped

        # Post-Wait signals
        self.postwait_start = self._postwait.start
        self.postwait_ended = self._postwait.ended
        self.postwait_paused = self._postwait.paused
        self.postwait_stopped = self._postwait.stopped

        # Fade signals
        self.fadein_start = Signal()
        self.fadein_end = Signal()
        self.fadeout_start = Signal()
        self.fadeout_end = Signal()

        # Status signals
        self.interrupted = Signal()  # self
        self.started = Signal()  # self
        self.stopped = Signal()  # self
        self.paused = Signal()  # self
        self.error = Signal()  # self
        self.next = Signal()  # self
        self.end = Signal()  # self

        self.changed("next_action").connect(self.__next_action_changed)

    def execute(self, action=CueAction.Default):
        """Execute the specified action, if supported.

        .. Note::
            Even if not specified in Cue.CueActions, when CueAction.Default
            is given, a "default" action is selected depending on the current
            cue state, if this action is not supported nothing will be done.

        :param action: the action to be performed
        :type action: CueAction
        """
        if action == CueAction.Default:
            if self._state & CueState.IsRunning:
                action = CueAction(self.default_stop_action)
            else:
                action = CueAction(self.default_start_action)

        if action == CueAction.DoNothing:
            return

        if action in self.CueActions:
            if action == CueAction.Interrupt:
                self.interrupt()
            elif action == CueAction.FadeOutInterrupt:
                self.interrupt(fade=True)
            elif action == CueAction.Start:
                self.start()
            elif action == CueAction.FadeInStart:
                self.start(fade=self.fadein_duration > 0)
            elif action == CueAction.Stop:
                self.stop()
            elif action == CueAction.FadeOutStop:
                self.stop(fade=self.fadeout_duration > 0)
            elif action == CueAction.Pause:
                self.pause()
            elif action == CueAction.FadeOutPause:
                self.pause(fade=self.fadeout_duration > 0)
            elif action == CueAction.Resume:
                self.resume()
            elif action == CueAction.FadeInResume:
                self.resume(fade=self.fadein_duration > 0)
            elif action == CueAction.FadeOut:
                duration = AppConfig().get("cue.fadeAction", 0)
                fade = AppConfig().get(
                    "cue.fadeActionType", FadeOutType.Linear.name
                )

                self.fadeout(duration, FadeOutType[fade])
            elif action == CueAction.FadeIn:
                duration = AppConfig().get("cue.fadeAction", 0)
                fade = AppConfig().get(
                    "cue.fadeActionType", FadeInType.Linear.name
                )

                self.fadein(duration, FadeInType[fade])

    @async_function
    def start(self, fade=False):
        """Start the cue."""

        # If possible acquire the state-lock, otherwise return
        if not self._st_lock.acquire(blocking=False):
            return

        try:
            # If we are already running release and return
            if self._state & CueState.IsRunning:
                return

            state = self._state

            # PreWait
            if self.pre_wait and state & (
                CueState.IsStopped | CueState.PreWait_Pause
            ):
                self._state = CueState.PreWait
                # Start the wait, the lock is released during the wait and
                # re-acquired after
                if not self._prewait.wait(self.pre_wait, lock=self._st_lock):
                    # PreWait interrupted, check the state to be correct
                    if self._state & CueState.PreWait:
                        self._state ^= CueState.PreWait
                    return

            # Cue-Start (still locked), the __start__ function should not block
            if state & (
                CueState.IsStopped | CueState.Pause | CueState.PreWait_Pause
            ):

                running = self.__start__(fade)
                self._state = CueState.Running
                self.started.emit(self)

                if not running:
                    self._ended()

            # PostWait (still locked)
            if state & (
                CueState.IsStopped
                | CueState.PreWait_Pause
                | CueState.PostWait_Pause
            ):
                if (
                    self.next_action == CueNextAction.TriggerAfterWait
                    or self.next_action == CueNextAction.SelectAfterWait
                ):
                    self._state |= CueState.PostWait

                    if self._postwait.wait(self.post_wait, lock=self._st_lock):
                        # PostWait ended
                        self._state ^= CueState.PostWait
                        self.next.emit(self)
                    elif self._state & CueState.PostWait:
                        # PostWait interrupted, check the state to be correct
                        self._state ^= CueState.PostWait

                    # If the cue was only post-waiting we remain with
                    # an invalid state
                    if not self._state:
                        self._state = CueState.Stop
        finally:
            self._st_lock.release()

    def resume(self, fade=False):
        """Restart the cue if paused."""
        if self._state & CueState.IsPaused:
            self.start(fade)

    def __start__(self, fade=False):
        """Implement the cue `start` behavior.

        Long running task should not block this function (i.e. the fade should
        be performed in another thread).

        When called from `Cue.start()`, `_st_lock` is acquired.

        If the execution is instantaneous, should return False, otherwise
        return True and call the `_ended` function later.

        :param fade: True if a fade should be performed (when supported)
        :type fade: bool
        :return: False if the cue is already terminated, True otherwise
            (e.g. asynchronous execution)
        :rtype: bool
        """
        return False

    @async_function
    def stop(self, fade=False):
        """Stop the cue."""

        # If possible acquire the state-lock, otherwise return
        if not self._st_lock.acquire(blocking=False):
            return

        try:
            # Stop PreWait (if in PreWait(_Pause) nothing else is "running")
            if self._state & (CueState.PreWait | CueState.PreWait_Pause):
                self._state = CueState.Stop
                self._prewait.stop()
            else:
                # Stop PostWait
                if self._state & (CueState.PostWait | CueState.PostWait_Pause):
                    # Remove PostWait or PostWait_Pause state
                    self._state = (self._state ^ CueState.PostWait) & (
                        self._state ^ CueState.PostWait_Pause
                    )
                    self._postwait.stop()

                # Stop the cue
                if self._state & (CueState.Running | CueState.Pause):
                    # Here the __stop__ function should release and re-acquire
                    # the state-lock during a fade operation
                    if not self.__stop__(fade):
                        # Stop operation interrupted
                        return

                    # Remove Running or Pause state
                    self._state = (self._state ^ CueState.Running) & (
                        self._state ^ CueState.Pause
                    )
                    self._state |= CueState.Stop
                    self.stopped.emit(self)
        finally:
            self._st_lock.release()

    def __stop__(self, fade=False):
        """Implement the cue `stop` behavior.

        Long running task should block this function (i.e. the fade should
        "block" this function), when this happen `_st_lock` must be released and
        then re-acquired.

        If called during a `fadeout` operation this should be interrupted,
        the cue stopped and return `True`.

        :param fade: True if a fade should be performed (when supported)
        :type fade: bool
        :return: False if interrupted, True otherwise
        :rtype: bool
        """
        return False

    @async_function
    def pause(self, fade=False):
        """Pause the cue."""

        # If possible acquire the state-lock, otherwise return
        if not self._st_lock.acquire(blocking=False):
            return

        try:
            # Pause PreWait (if in PreWait nothing else is "running")
            if self._state & CueState.PreWait:
                self._state ^= CueState.PreWait
                self._state |= CueState.PreWait_Pause
                self._prewait.pause()
            else:
                # Pause PostWait
                if self._state & CueState.PostWait:
                    self._state ^= CueState.PostWait
                    self._state |= CueState.PostWait_Pause
                    self._postwait.pause()

                # Pause the cue
                if self._state & CueState.Running:
                    # Here the __pause__ function should release and re-acquire
                    # the state-lock during a fade operation
                    if not self.__pause__(fade):
                        return

                    self._state ^= CueState.Running
                    self._state |= CueState.Pause
                    self.paused.emit(self)
        finally:
            self._st_lock.release()

    def __pause__(self, fade=False):
        """Implement the cue `pause` behavior.

        Long running task should block this function (i.e. the fade should
        "block" this function), when this happen `_st_lock` must be released and
        then re-acquired.

        If called during a `fadeout` operation this should be interrupted,
        the cue paused and return `True`.

        If during the execution the fade operation is interrupted this function
        must return `False`.

        :param fade: True if a fade should be performed (when supported)
        :type fade: bool
        :return: False if interrupted, True otherwise
        :rtype: bool
        """
        return False

    @async_function
    def interrupt(self, fade=False):
        """Interrupt the cue.

        :param fade: True if a fade should be performed (when supported)
        :type fade: bool
        """
        with self._st_lock:
            # Stop PreWait (if in PreWait(_Pause) nothing else is "running")
            if self._state & (CueState.PreWait | CueState.PreWait_Pause):
                self._state = CueState.Stop
                self._prewait.stop()
            else:
                # Stop PostWait
                if self._state & (CueState.PostWait | CueState.PostWait_Pause):
                    # Remove PostWait or PostWait_Pause state
                    self._state = (self._state ^ CueState.PostWait) & (
                        self._state ^ CueState.PostWait_Pause
                    )
                    self._postwait.stop()

                # Interrupt the cue
                if self._state & (CueState.Running | CueState.Pause):
                    self.__interrupt__(fade)

                    # Remove Running or Pause state
                    self._state = (self._state ^ CueState.Running) & (
                        self._state ^ CueState.Pause
                    )
                    self._state |= CueState.Stop
                    self.interrupted.emit(self)

    def __interrupt__(self, fade=False):
        """Implement the cue `interrupt` behavior.

        Long running task should block this function without releasing
        `_st_lock`.

        :param fade: True if a fade should be performed (when supported)
        :type fade: bool
        """

    def fadein(self, duration, fade_type):
        """Fade-in the cue.

        :param duration: How much the fade should be long (in seconds)
        :type duration: float
        :param fade_type: The fade type
        :type fade_type: FadeInType
        """

    def fadeout(self, duration, fade_type):
        """Fade-out the cue.

        :param duration: How much the fade should be long (in seconds)
        :type duration: float
        :param fade_type: The fade type
        :type fade_type: FadeOutType
        """

    def _ended(self):
        """Remove the Running state, if needed set it to Stop."""
        locked = self._st_lock.acquire(blocking=False)

        if self._state == CueState.Running:
            self._state = CueState.Stop
        else:
            self._state ^= CueState.Running

        self.end.emit(self)

        if locked:
            self._st_lock.release()

    def _error(self):
        """Remove Running/Pause/Stop state and add Error state."""
        locked = self._st_lock.acquire(blocking=False)

        self._state = (
            (self._state ^ CueState.Running)
            & (self._state ^ CueState.Pause)
            & (self._state ^ CueState.Stop)
        ) | CueState.Error

        self.error.emit(self)

        if locked:
            self._st_lock.release()

    def current_time(self):
        """Return the current execution time if available, otherwise 0.

        :rtype: int
        """
        return 0

    def prewait_time(self):
        return self._prewait.current_time()

    def postwait_time(self):
        return self._postwait.current_time()

    @property
    def state(self):
        """Return the current state.

        :rtype: int
        """
        return self._state

    def __next_action_changed(self, next_action):
        self.end.disconnect(self.next.emit)
        if (
            next_action == CueNextAction.TriggerAfterEnd
            or next_action == CueNextAction.SelectAfterEnd
        ):
            self.end.connect(self.next.emit)
