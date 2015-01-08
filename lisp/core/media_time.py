##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtCore import pyqtSignal, QObject
from lisp.core.media import Media

from lisp.core.clock import Clock


class MediaTime(QObject):

    notify = pyqtSignal(int)

    def __init__(self, media):
        super().__init__()

        self._media = media
        self._clock = Clock()

        # Media "status" signals
        self._media.on_play.connect(self._on_play)
        self._media.paused.connect(self._on_pause)
        self._media.stopped.connect(self._on_stop)
        self._media.interrupted.connect(self._on_stop)
        self._media.error.connect(self._on_stop)
        self._media.eos.connect(self._on_stop)

        if self._media.state == Media.PLAYING:
            self._on_play()

    def _notify(self):
        '''Notify the current media time'''
        self.notify.emit(self._media.current_time())

    def _on_pause(self):
        try:
            self._clock.remove_callback(self._notify)
        except Exception:
            pass

    def _on_play(self):
        self._clock.add_callback(self._notify)

    def _on_stop(self):
        try:
            self._clock.remove_callback(self._notify)
        except Exception:
            pass
        finally:
            self.notify.emit(-1)
