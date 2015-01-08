##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5 import QtCore
from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import *  # @UnusedWildImport

from lisp.ui.settings.sections.cue_general import CueGeneral


class MediaCueGeneral(CueGeneral):

    Name = 'Cue Settings'

    def __init__(self, size, cue=None, parent=None):
        super().__init__(size, cue=cue, parent=parent)

        # Start at
        self.startGroup = QGroupBox(self)
        self.startGroup.setLayout(QHBoxLayout())

        self.startEdit = QTimeEdit(self.startGroup)
        self.startEdit.setDisplayFormat('HH.mm.ss.zzz')
        self.startGroup.layout().addWidget(self.startEdit)

        self.startLabel = QLabel(self.startGroup)
        self.startLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.startGroup.layout().addWidget(self.startLabel)

        self.layout().addWidget(self.startGroup)

        # Loop
        self.loopGroup = QGroupBox(self)
        self.loopGroup.setLayout(QHBoxLayout())

        self.spinLoop = QSpinBox(self.loopGroup)
        self.spinLoop.setRange(-1, 1000000)
        self.loopGroup.layout().addWidget(self.spinLoop)

        self.loopLabel = QLabel(self.loopGroup)
        self.loopLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.loopGroup.layout().addWidget(self.loopLabel)

        self.layout().addWidget(self.loopGroup)

        # Checks
        self.checkPause = QCheckBox(self)
        self.layout().addWidget(self.checkPause)

        self.retranslateUi()

    def retranslateUi(self):
        self.startGroup.setTitle('Start time')
        self.startLabel.setText('Amount of skip time')
        self.loopGroup.setTitle("Loop")
        self.loopLabel.setText("Repetition after first play (-1 = infinite)")
        self.checkPause.setText("Enable Pause")

    def get_configuration(self):
        conf = super().get_configuration()
        conf['media'] = {}

        checkable = self.startGroup.isCheckable()

        if not (checkable and not self.startGroup.isChecked()):
            time = self.startEdit.time().msecsSinceStartOfDay()
            conf['media']['start_at'] = time
        if not (checkable and not self.loopGroup.isChecked()):
            conf['media']['loop'] = self.spinLoop.value()
        if self.checkPause.checkState() != QtCore.Qt.PartiallyChecked:
            conf['pause'] = self.checkPause.isChecked()

        return conf

    def enable_check(self, enable):
        super().enable_check(enable)

        self.startGroup.setCheckable(enable)
        self.startGroup.setChecked(False)

        self.loopGroup.setCheckable(enable)
        self.loopGroup.setChecked(False)

        self.checkPause.setTristate(enable)
        if enable:
            self.checkPause.setCheckState(QtCore.Qt.PartiallyChecked)

    def set_configuration(self, conf):
        super().set_configuration(conf)

        if 'pause' in conf:
            self.checkPause.setChecked(conf['pause'])
        if 'media' in conf:
            if 'loop' in conf['media']:
                self.spinLoop.setValue(conf['media']['loop'])
            if 'duration' in conf['media'] and conf['media']['duration'] > 0:
                t = QTime().fromMSecsSinceStartOfDay(conf['media']['duration'])
                self.startEdit.setMaximumTime(t)
            if 'start_at' in conf['media']:
                t = QTime().fromMSecsSinceStartOfDay(conf['media']['start_at'])
                self.startEdit.setTime(t)
