import datetime

from lisp.core.clock import Clock
from lisp.cues.cue import Cue


class ClockCue(Cue):

    Name = 'Clock Cue'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.__running = False
        self.name = '00:00:00'

    def finalize(self):
        if self.__running:
            self._stop()

    def execute(self, action=Cue.CueAction.Default):
        if not self.__running:
            self._start()
        else:
            self._stop()

    def _time_update(self):
        self.name = datetime.datetime.now().strftime('%H:%M:%S')

    def _start(self):
        Clock().add_callback(self._time_update)
        self.__running = True

    def _stop(self):
        Clock().remove_callback(self._time_update)
        self.__running = False
        self.name = '00:00:00'
