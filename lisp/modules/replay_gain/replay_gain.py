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

import logging
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed as futures_completed
from math import pow
from threading import Thread, Lock

import gi

from lisp.ui.ui_utils import translate

gi.require_version('Gst', '1.0')
from gi.repository import Gst
from PyQt5.QtWidgets import QMenu, QAction, QDialog

from lisp.application import Application
from lisp.core.action import Action
from lisp.core.actions_handler import MainActionsHandler
from lisp.core.module import Module
from lisp.core.signal import Signal, Connection
from lisp.cues.media_cue import MediaCue
from lisp.ui.mainwindow import MainWindow
from .gain_ui import GainUi, GainProgressDialog


class GainAction(Action):
    __slots__ = ('__media_list', '__new_volumes', '__old_volumes')

    def __init__(self):
        self.__media_list = []
        self.__new_volumes = []
        self.__old_volumes = []

    def add_media(self, media, new_volume):
        volume = media.element('Volume')
        if volume is not None:
            self.__media_list.append(media)
            self.__new_volumes.append(new_volume)
            self.__old_volumes.append(volume.normal_volume)

    def do(self):
        for n, media in enumerate(self.__media_list):
            volume = media.element('Volume')
            if volume is not None:
                volume.normal_volume = self.__new_volumes[n]

    def undo(self):
        for n, media in enumerate(self.__media_list):
            volume = media.element('Volume')
            if volume is not None:
                volume.normal_volume = self.__old_volumes[n]

    def redo(self):
        self.do()

    def log(self):
        return 'Replay gain volume adjusted'


class GainMainThread(Thread):
    MAX_GAIN = 20  # dB

    def __init__(self, files, threads, mode, ref_level, norm_level):
        super().__init__()
        self.setDaemon(True)

        self._futures = {}
        self._running = False
        self._action = GainAction()

        # file -> media {'filename1': [media1, media2], 'filename2': [media3]}
        self.files = files
        self.threads = threads
        self.mode = mode
        self.ref_level = ref_level
        self.norm_level = norm_level

        self.on_progress = Signal()

    def stop(self):
        self._running = False
        for future in self._futures:
            self._futures[future].stop()
            future.cancel()

    def run(self):
        self._running = True

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            for file in self.files.keys():
                gain = GstGain(file, self.ref_level)
                self._futures[executor.submit(gain.gain)] = gain

            for future in futures_completed(self._futures):
                if self._running:
                    try:
                        self._post_process(*future.result())
                    except Exception:
                        # Call with the value stored in the GstGain object
                        self._post_process(*self._futures[future].result)
                else:
                    break

        if self._running:
            MainActionsHandler.do_action(self._action)
        else:
            logging.info('REPLY-GAIN:: Stopped by user')

        self.on_progress.emit(-1)
        self.on_progress.disconnect()

    def _post_process(self, gained, gain, peak, uri):
        if gained:
            if gain > self.MAX_GAIN:
                gain = self.MAX_GAIN

            if self.mode == 0:
                volume = min(1 / peak, pow(10, gain / 20))
            else:  # (self.mode == 1)
                volume = 1 / peak * pow(10, self.norm_level / 20)

            for media in self.files[uri]:
                self._action.add_media(media, volume)

            logging.info('REPLY-GAIN:: completed ' + uri)
        else:
            logging.error('REPLY-GAIN:: failed  ' + uri)

        self.on_progress.emit(1)


class ReplayGain(Module):
    Name = 'ReplayGain'

    def __init__(self):
        self._gain_thread = None

        # Entry in mainWindow menu
        self.menu = QMenu(translate('ReplayGain',
                                    'ReplayGain / Normalization'))
        self.menu_action = MainWindow().menuTools.addMenu(self.menu)

        self.actionGain = QAction(MainWindow())
        self.actionGain.triggered.connect(self.gain)
        self.actionGain.setText(translate('ReplayGain', 'Calculate'))
        self.menu.addAction(self.actionGain)

        self.actionReset = QAction(MainWindow())
        self.actionReset.triggered.connect(self._reset_all)
        self.actionReset.setText(translate('ReplayGain', 'Reset all'))
        self.menu.addAction(self.actionReset)

        self.actionResetSelected = QAction(MainWindow())
        self.actionResetSelected.triggered.connect(self._reset_selected)
        self.actionResetSelected.setText(translate('ReplayGain',
                                                   'Reset selected'))
        self.menu.addAction(self.actionResetSelected)

    def gain(self):
        gainUi = GainUi(MainWindow())
        gainUi.exec_()

        if gainUi.result() == QDialog.Accepted:

            files = {}
            if gainUi.only_selected():
                cues = Application().layout.get_selected_cues(MediaCue)
            else:
                cues = Application().cue_model.filter(MediaCue)

            for cue in cues:
                media = cue.media
                uri = media.input_uri()
                if uri is not None:
                    if uri not in files:
                        files[uri] = [media]
                    else:
                        files[uri].append(media)

            # Gain (main) thread
            self._gain_thread = GainMainThread(files, gainUi.threads(),
                                               gainUi.mode(),
                                               gainUi.ref_level(),
                                               gainUi.norm_level())

            # Progress dialog
            self._progress = GainProgressDialog(len(files))
            self._gain_thread.on_progress.connect(self._progress.on_progress,
                                                  mode=Connection.QtQueued)

            self._progress.show()
            self._gain_thread.start()

    def stop(self):
        if self._gain_thread is not None:
            self._gain_thread.stop()

    def terminate(self):
        self.stop()
        MainWindow().menuTools.removeAction(self.menu_action)

    def _reset_all(self):
        self._reset(Application().cue_model.filter(MediaCue))

    def _reset_selected(self):
        self._reset(Application().cue_model.filter(MediaCue))

    def _reset(self, cues):
        action = GainAction()
        for cue in cues:
            action.add_media(cue.media, 1.0)
        MainActionsHandler.do_action(action)


class GstGain:
    def __init__(self, uri, ref_level):
        self.__lock = Lock()

        self.uri = uri
        self.ref_level = ref_level
        self.result = (False, 0, 0, uri)
        self.gain_pipe = None

    # Create a pipeline with a fake audio output and get the gain levels
    def gain(self):
        pipe = 'uridecodebin uri="{0}" ! audioconvert ! rganalysis \
                reference-level={1} ! fakesink'.format(self.uri, self.ref_level)
        self.gain_pipe = Gst.parse_launch(pipe)

        gain_bus = self.gain_pipe.get_bus()
        gain_bus.add_signal_watch()
        gain_bus.connect('message', self._on_message)

        logging.info('REPLY-GAIN:: started ' + str(self.uri))
        self.gain_pipe.set_state(Gst.State.PLAYING)

        # Block here until EOS
        self.__lock.acquire(False)
        self.__lock.acquire()

        # Reset the pipe
        self.gain_pipe = None

        # Return the computation result
        return self.result

    def stop(self):
        if self.gain_pipe is not None:
            self.gain_pipe.send_event(Gst.Event.new_eos())

    def _on_message(self, bus, message):
        try:
            if message.type == Gst.MessageType.EOS and self.__lock.locked():
                self.__lock.release()
            elif message.type == Gst.MessageType.TAG:
                tags = message.parse_tag()
                tag = tags.get_double(Gst.TAG_TRACK_GAIN)
                peak = tags.get_double(Gst.TAG_TRACK_PEAK)

                if tag[0] and peak[0]:
                    self.gain_pipe.set_state(Gst.State.NULL)
                    self.result = (True, tag[1], peak[1], self.uri)

                    if self.__lock.locked():
                        self.__lock.release()
            elif message.type == Gst.MessageType.ERROR:
                logging.debug('REPLY-GAIN:: ' + str(message.parse_error()))

                self.gain_pipe.set_state(Gst.State.NULL)

                if self.__lock.locked():
                    self.__lock.release()
        except Exception:
            if self.__lock.locked():
                self.__lock.release()
