##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed as futures_completed
import logging
from math import pow
from os import cpu_count
from threading import Thread, Lock

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *  # @UnusedWildImport
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
from lisp.core.plugin import Plugin

from lisp.actions.action import Action
from lisp.actions.actions_handler import ActionsHandler
from lisp.application import Application
from lisp.cues.media_cue import MediaCue


class GainAction(Action):

    def __init__(self):
        self._mediaList = []
        self._newVolumes = []
        self._oldVolumes = []

    def add_media(self, media, new_volume):
        volume = media.element('Volume')
        if volume is not None:
            self._mediaList.append(media)
            self._newVolumes.append(new_volume)
            self._oldVolumes.append(volume.properties()['normal_volume'])

    def do(self):
        for n, media in enumerate(self._mediaList):
            volume = media.element('Volume')
            if volume is not None:
                volume.set_property('normal_volume', self._newVolumes[n])

    def undo(self):
        for n, media in enumerate(self._mediaList):
            volume = media.element('Volume')
            if volume is not None:
                volume.set_property('normal_volume', self._oldVolumes[n])

    def redo(self):
        self.do()

    def log(self):
        return 'Replay gain volume adjust'


class ReplayGain(QtCore.QObject, Plugin):

    Name = 'ReplayGain'

    MAX_GAIN = 20  # dB

    on_progress = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.app = Application()

        # file -> media {"filename1": [media1, media2], "filename2": [media3]}
        self._file_to_gain = {}
        self._futures = {}
        self._stopped = False

        # Voice in mainWindow menu
        self.menu = QMenu("ReplayGain / Normalization")
        self.menu_action = self.app.mainWindow.menuTools.addMenu(self.menu)

        self.actionGain = QAction(self.app.mainWindow)
        self.actionGain.triggered.connect(self.gain)
        self.actionGain.setText("Calculate")
        self.menu.addAction(self.actionGain)

        self.actionReset = QAction(self.app.mainWindow)
        self.actionReset.triggered.connect(self._reset_all)
        self.actionReset.setText("Reset all")
        self.menu.addAction(self.actionReset)

        self.actionResetSelected = QAction(self.app.mainWindow)
        self.actionResetSelected.triggered.connect(self._reset_selected)
        self.actionResetSelected.setText("Reset selected")
        self.menu.addAction(self.actionResetSelected)

        self._setup_progress_dialog()

        self.on_progress.connect(self._on_progress, Qt.QueuedConnection)

    def gain(self):
        gainUi = GainUi(self.app.mainWindow)
        gainUi.exec_()

        self._file_to_gain.clear()
        if gainUi.result() == QDialog.Accepted:
            self.gainSelctedMode = gainUi.checkBox.isChecked()

            if(self.gainSelctedMode):
                cues = self.app.mainWindow.layout.get_selected_cues(MediaCue)
            else:
                cues = self.app.mainWindow.layout.get_cues(MediaCue)

            for cue in cues:
                media = cue.media
                if media.input_uri() is not None:
                    if media.input_uri() not in self._file_to_gain:
                        self._file_to_gain[media.input_uri()] = [media]
                    else:
                        self._file_to_gain[media.input_uri()].append(media)

            self._gain_mode = gainUi.gain_mode()
            self._norm_level = gainUi.norm_level()
            self._ref_level = gainUi.ref_level()
            self._threads = gainUi.threads()

            self.progress.reset()
            self.progress.setRange(1, len(self._file_to_gain))

            self._calc_gain()

    def reset(self):
        self.stop()
        self.app.mainWindow.menuTools.removeAction(self.menu_action)

    def stop(self):
        self._stopped = True
        for future in self._futures:
            self._futures[future].stop()
            future.cancel()

    def _reset_all(self):
        self._reset(self.app.layout.get_cues(MediaCue))

    def _reset_selected(self):
        self._reset(self.app.layout.get_selected_cues(MediaCue))

    def _reset(self, cues):
        action = GainAction()
        for cue in cues:
            action.add_media(cue.media, 1.0)
        ActionsHandler().do_action(action)

    def _calc_gain(self):
        self.progress.setLabelText('Analysis ...')
        self.progress.show()

        self._thread = Thread(target=self._exec, daemon=True)
        self._thread.setName('ReplayGainThread')
        self._thread.start()

    def _exec(self):
        self._futures = {}
        self._stopped = False
        self._action = GainAction()

        with ThreadPoolExecutor(max_workers=self._threads) as executor:
            for file in self._file_to_gain.keys():
                gain = GstGain(file, self._ref_level)
                self._futures[executor.submit(gain.gain)] = gain
            for future in futures_completed(self._futures):
                if not self._stopped:
                    try:
                        self._apply_gain(*future.result())
                    except Exception:
                        # Call with the value stored in the GstGain object
                        self._apply_gain(*self._futures[future].result)
                else:
                    break

        if not self._stopped:
            ActionsHandler().do_action(self._action)
        else:
            logging.info('REPLY-GAIN:: Stopped by user')

        self.on_progress.emit(-1)

    def _apply_gain(self, gained, gain, peak, uri):
        if gained:
            if(gain > ReplayGain.MAX_GAIN):
                gain = ReplayGain.MAX_GAIN

            if self._gain_mode == 0:
                volume = min(1 / peak, pow(10, (gain) / 20))
            elif self._gain_mode == 1:
                volume = 1 / peak * pow(10, (self._norm_level) / 20)

            for media in self._file_to_gain[uri]:
                self._action.add_media(media, volume)

            logging.info('REPLY-GAIN:: completed ' + uri)
        else:
            logging.error('REPLY-GAIN:: failed  ' + uri)

        self.on_progress.emit(1)

    def _setup_progress_dialog(self):
        self.progress = QProgressDialog()
        # self.progress.setWindowModality(QtCore.Qt.ApplicationModal)
        self.progress.setWindowTitle('ReplayGain / Normalization')
        self.progress.setMaximumSize(320, 110)
        self.progress.setMinimumSize(320, 110)
        self.progress.resize(320, 110)
        self.progress.canceled.connect(self.stop)

    def _on_progress(self, value):
        if value == -1:
            # Hide the progress dialog
            self.progress.setValue(self.progress.maximum())
            # But sometimes the dialog freezes, and it must be destroyed
            self.progress.deleteLater()
            self._setup_progress_dialog()
        else:
            self.progress.setValue(self.progress.value() + value)


class GstGain:

    def __init__(self, uri, ref_level):
        self.__lock = Lock()

        self.uri = uri
        self.ref_level = ref_level
        self.result = (False, 0, 0, uri)
        self.gain_pipe = None

    # Create a pipeline with a fake audio output and get, the gain levels
    def gain(self):
        pipe = ('uridecodebin uri="' + self.uri + '" ! audioconvert ! ' +
                'rganalysis reference-level=' + str(self.ref_level) +
                ' ! fakesink')
        self.gain_pipe = Gst.parse_launch(pipe)

        gain_bus = self.gain_pipe.get_bus()
        gain_bus.add_signal_watch()
        gain_bus.connect("message", self._on_message)

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


class GainUi(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setMaximumSize(380, 210)
        self.setMinimumSize(380, 210)
        self.resize(380, 210)

        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 5, 360, 210))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)

        self.horizontalLayout_2 = QHBoxLayout()

        self.radioButton = QRadioButton(self.verticalLayoutWidget)
        self.radioButton.setChecked(True)
        self.horizontalLayout_2.addWidget(self.radioButton)

        self.spinBox = QSpinBox(self.verticalLayoutWidget)
        self.spinBox.setMaximum(150)
        self.spinBox.setValue(89)
        self.horizontalLayout_2.addWidget(self.spinBox)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()

        self.radioButton_2 = QRadioButton(self.verticalLayoutWidget)
        self.horizontalLayout.addWidget(self.radioButton_2)

        self.spinBox_2 = QSpinBox(self.verticalLayoutWidget)
        self.spinBox_2.setMinimum(-100)
        self.spinBox_2.setMaximum(0)
        self.spinBox_2.setEnabled(False)
        self.horizontalLayout.addWidget(self.spinBox_2)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.checkBox = QCheckBox(self.verticalLayoutWidget)
        self.verticalLayout.addWidget(self.checkBox)

        self.line = QFrame(self.verticalLayoutWidget)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.verticalLayout.addWidget(self.line)

        self.horizontalLayout_4 = QHBoxLayout()

        self.label_3 = QLabel(self.verticalLayoutWidget)
        self.horizontalLayout_4.addWidget(self.label_3)

        self.spinBox_3 = QSpinBox(self.verticalLayoutWidget)
        self.spinBox_3.setMinimum(1)
        try:
            self.spinBox_3.setMaximum(cpu_count())
            self.spinBox_3.setValue(cpu_count())
        except Exception:
            self.spinBox_3.setMaximum(1)
            self.spinBox_3.setValue(1)
        self.horizontalLayout_4.addWidget(self.spinBox_3)

        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()

        self.pushButton_3 = QPushButton(self.verticalLayoutWidget)
        self.horizontalLayout_3.addWidget(self.pushButton_3)

        self.pushButton_2 = QPushButton(self.verticalLayoutWidget)
        self.horizontalLayout_3.addWidget(self.pushButton_2)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.buttonGroup = QButtonGroup()
        self.buttonGroup.addButton(self.radioButton)
        self.buttonGroup.addButton(self.radioButton_2)

        self.radioButton_2.toggled.connect(self.spinBox_2.setEnabled)
        self.radioButton_2.toggled.connect(self.spinBox.setDisabled)

        self.pushButton_3.clicked.connect(self.reject)
        self.pushButton_2.clicked.connect(self.accept)

        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle("ReplayGain / Normalization")
        self.label_3.setText("Threads number")
        self.checkBox.setText("Apply only to selected media")
        self.radioButton.setText("ReplayGain to (dB SPL)")
        self.radioButton_2.setText("Normalize to (dB)")
        self.pushButton_2.setText("Apply")
        self.pushButton_3.setText("Cancel")

    def gain_mode(self):
        return -(self.buttonGroup.checkedId() + 2)

    def norm_level(self):
        return self.spinBox_2.value()

    def ref_level(self):
        return self.spinBox.value()

    def threads(self):
        return self.spinBox_3.value()
