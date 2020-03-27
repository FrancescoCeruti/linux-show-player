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

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Thread, Lock

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst
from PyQt5.QtWidgets import QMenu, QAction, QDialog

from lisp.command.command import Command
from lisp.core.plugin import Plugin
from lisp.core.signal import Signal, Connection
from lisp.cues.media_cue import MediaCue
from lisp.ui.ui_utils import translate
from .gain_ui import GainUi, GainProgressDialog

logger = logging.getLogger(__name__)


class ReplayGain(Plugin):
    Name = "ReplayGain / Normalization"
    Authors = ("Francesco Ceruti",)
    Description = "Allow to normalize cues volume"

    RESET_VALUE = 1.0

    def __init__(self, app):
        super().__init__(app)
        self._gain_thread = None

        # Entry in mainWindow menu
        self.menu = QMenu(translate("ReplayGain", "ReplayGain / Normalization"))
        self.menu_action = self.app.window.menuTools.addMenu(self.menu)

        self.actionGain = QAction(self.app.window)
        self.actionGain.triggered.connect(self.gain)
        self.actionGain.setText(translate("ReplayGain", "Calculate"))
        self.menu.addAction(self.actionGain)

        self.actionReset = QAction(self.app.window)
        self.actionReset.triggered.connect(self._reset_all)
        self.actionReset.setText(translate("ReplayGain", "Reset all"))
        self.menu.addAction(self.actionReset)

        self.actionResetSelected = QAction(self.app.window)
        self.actionResetSelected.triggered.connect(self._reset_selected)
        self.actionResetSelected.setText(
            translate("ReplayGain", "Reset selected")
        )
        self.menu.addAction(self.actionResetSelected)

    def gain(self):
        gainUi = GainUi(self.app.window)
        gainUi.exec()

        if gainUi.result() == QDialog.Accepted:
            if gainUi.only_selected():
                cues = self.app.layout.selected_cues(MediaCue)
            else:
                cues = self.app.cue_model.filter(MediaCue)

            # Extract single uri(s), this way if a uri is used in more than
            # one place, the gain is only calculated once.
            files = {}
            for cue in cues:
                media = cue.media
                uri = media.input_uri()

                if uri is not None:
                    if uri[:7] == "file://":
                        uri = "file://" + self.app.session.abs_path(uri[7:])

                    if uri not in files:
                        files[uri] = [media]
                    else:
                        files[uri].append(media)

            # Gain (main) thread
            self._gain_thread = GainMainThread(
                self.app.commands_stack,
                files,
                gainUi.threads(),
                gainUi.mode(),
                gainUi.ref_level(),
                gainUi.norm_level(),
            )

            # Progress dialog
            self._progress = GainProgressDialog(len(files))
            self._gain_thread.on_progress.connect(
                self._progress.on_progress, mode=Connection.QtQueued
            )

            self._progress.show()
            self._gain_thread.start()

    def stop(self):
        if self._gain_thread is not None:
            self._gain_thread.stop()

    def terminate(self):
        self.stop()
        self.app.window.menuTools.removeAction(self.menu_action)

    def _reset_all(self):
        self._reset(self.app.cue_model.filter(MediaCue))

    def _reset_selected(self):
        self._reset(self.app.layout.selected_cues(MediaCue))

    def _reset(self, cues):
        action = UpdateGainCommand()
        for cue in cues:
            action.add_media(cue.media, ReplayGain.RESET_VALUE)

        self.app.commands_stack.do(action)


class UpdateGainCommand(Command):
    __slots__ = ("_media_list", "_new_volumes", "_old_volumes")

    def __init__(self):
        self._media_list = []
        self._new_volumes = []
        self._old_volumes = []

    def add_media(self, media, new_volume):
        volume_element = media.element("Volume")
        if volume_element is not None:
            self._media_list.append(media)
            self._new_volumes.append(new_volume)
            self._old_volumes.append(volume_element.normal_volume)

    def do(self):
        self.__update(self._new_volumes)

    def undo(self):
        self.__update(self._old_volumes)

    def __update(self, volumes):
        for media, volume in zip(self._media_list, volumes):
            volume_element = media.element("Volume")
            if volume_element is not None:
                volume_element.normal_volume = volume

    def log(self):
        return "Replay gain volume adjusted."


class GainMainThread(Thread):
    def __init__(
        self, commands_stack, files, threads, mode, ref_level, norm_level
    ):
        super().__init__()
        self.setDaemon(True)

        self._commands_stack = commands_stack
        self._update_command = UpdateGainCommand()
        self._running = False
        self._futures = {}

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

            for future in as_completed(self._futures):
                if self._running:
                    try:
                        self._post_process(future.result())
                    except Exception:
                        logger.exception(
                            translate(
                                "ReplayGainError",
                                "An error occurred while processing gain results.",
                            )
                        )
                    finally:
                        self.on_progress.emit(1)
                else:
                    break

        if self._running:
            self._commands_stack.do(self._update_command)
        else:
            logger.info(
                translate("ReplayGainInfo", "Gain processing stopped by user.")
            )

        self.on_progress.emit(-1)
        self.on_progress.disconnect()

    def _post_process(self, gain):
        """
        :type gain: GstGain
        """
        if gain.completed:
            if self.mode == 0:
                volume = pow(10, gain.gain_value / 20)
            else:  # (self.mode == 1)
                volume = 1 / gain.peak_value * pow(10, self.norm_level / 20)

            for media in self.files[gain.uri]:
                self._update_command.add_media(media, volume)

            logger.debug(
                translate("ReplayGainDebug", "Applied gain for: {}").format(
                    gain.uri
                )
            )
        else:
            logger.debug(
                translate("ReplayGainDebug", "Discarded gain for: {}").format(
                    gain.uri
                )
            )


class GstGain:
    PIPELINE = (
        'uridecodebin uri="{0}" ! audioconvert ! rganalysis '
        "reference-level={1} ! fakesink"
    )

    def __init__(self, uri, ref_level):
        self.__lock = Lock()

        self.uri = uri
        self.ref_level = ref_level
        self.gain_pipe = None

        # Result attributes
        self.gain_value = 0
        self.peak_value = 0
        self.completed = False

    # Create a pipeline with a fake audio output and get the gain levels
    def gain(self):
        self.gain_pipe = Gst.parse_launch(
            GstGain.PIPELINE.format(self.uri, self.ref_level)
        )

        gain_bus = self.gain_pipe.get_bus()
        gain_bus.add_signal_watch()
        # Connect only the messages we want
        gain_bus.connect("message::eos", self._on_message)
        gain_bus.connect("message::tag", self._on_message)
        gain_bus.connect("message::error", self._on_message)

        self.gain_pipe.set_state(Gst.State.PLAYING)
        logger.info(
            translate(
                "ReplayGainInfo", "Started gain calculation for: {}"
            ).format(self.uri)
        )

        # Block here until EOS
        self.__lock.acquire(False)
        self.__lock.acquire()

        # Reset the pipe
        self.gain_pipe = None

        # Return the computation result
        return self

    def stop(self):
        if self.gain_pipe is not None:
            self.gain_pipe.send_event(Gst.Event.new_eos())

    def _on_message(self, bus, message):
        try:
            if message.type == Gst.MessageType.EOS:
                self.__release()
            elif message.type == Gst.MessageType.TAG:
                tags = message.parse_tag()
                tag = tags.get_double(Gst.TAG_TRACK_GAIN)
                peak = tags.get_double(Gst.TAG_TRACK_PEAK)

                if tag[0] and peak[0]:
                    self.gain_pipe.set_state(Gst.State.NULL)
                    # Save the gain results
                    self.gain_value = tag[1]
                    self.peak_value = peak[1]

                    logger.info(
                        translate(
                            "ReplayGainInfo", "Gain calculated for: {}"
                        ).format(self.uri)
                    )
                    self.completed = True
                    self.__release()
            elif message.type == Gst.MessageType.ERROR:
                error, _ = message.parse_error()
                self.gain_pipe.set_state(Gst.State.NULL)

                logger.error(f"GStreamer: {error.message}", exc_info=error)
                self.__release()
        except Exception:
            logger.exception(
                translate(
                    "ReplayGainError",
                    "An error occurred during gain calculation.",
                )
            )
            self.__release()

    def __release(self):
        if self.__lock.locked():
            self.__lock.release()
