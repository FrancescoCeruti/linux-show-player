##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *  # @UnusedWildImport
from lisp.utils.audio_utils import db_to_linear, linear_to_db

from lisp.gst.elements.volume import Volume
from lisp.ui.qmutebutton import QMuteButton
from lisp.ui.settings.section import SettingsSection


class VolumeSettings(SettingsSection):

    NAME = "Volume"
    ELEMENT = Volume

    def __init__(self, size, Id, parent=None):
        super().__init__(size, parent)

        self.id = Id
        self.normal = 1

        self.volumeBox = QGroupBox(self)
        self.volumeBox.setGeometry(0, 0, self.width(), 80)
        self.volumeBox.setLayout(QHBoxLayout())

        self.muteButton = QMuteButton(self.volumeBox)
        self.volumeBox.layout().addWidget(self.muteButton)

        self.volume = QSlider(self.volumeBox)
        self.volume.setRange(-1000, 100)
        self.volume.setPageStep(1)
        self.volume.setOrientation(Qt.Horizontal)
        self.volume.valueChanged.connect(self.volume_changed)
        self.volumeBox.layout().addWidget(self.volume)

        self.volumeLabel = QLabel(self.volumeBox)
        self.volumeLabel.setAlignment(Qt.AlignCenter)
        self.volumeBox.layout().addWidget(self.volumeLabel)

        self.volumeBox.layout().setStretch(0, 1)
        self.volumeBox.layout().setStretch(1, 4)
        self.volumeBox.layout().setStretch(2, 1)

        self.normalBox = QGroupBox(self)
        self.normalBox.setGeometry(0, 90, self.width(), 60)
        self.normalBox.setLayout(QHBoxLayout())

        self.normalLabel = QLabel(self.normalBox)
        self.normalLabel.setAlignment(Qt.AlignCenter)
        self.normalBox.layout().addWidget(self.normalLabel)

        self.normalReset = QCheckBox(self.normalBox)
        self.normalBox.layout().addWidget(self.normalReset)
        self.normalBox.layout().setAlignment(self.normalReset, Qt.AlignCenter)

        self.retranslateUi()

    def retranslateUi(self):
        self.volumeBox.setTitle("Volume")
        self.volumeLabel.setText("0.0 dB")
        self.normalBox.setTitle("Normalized volume")
        self.normalLabel.setText("0.0 dB")
        self.normalReset.setText("Reset")

    def enable_check(self, enable):
        for box in [self.normalBox, self.volumeBox]:
            box.setCheckable(enable)
            box.setChecked(False)

    def get_configuration(self):
        conf = {}
        checkable = self.volumeBox.isCheckable()

        if not (checkable and not self.volumeBox.isChecked()):
            conf["volume"] = db_to_linear(self.volume.value() / 10)
            conf["mute"] = self.muteButton.isMute()
        if not (checkable and not self.normalBox.isChecked()):
            if self.normalReset.isChecked():
                conf["normal_volume"] = 1
            else:
                conf["normal_volume"] = self.normal

        return {self.id: conf}

    def set_configuration(self, conf):
        if conf is not None and self.id in conf:
            self.volume.setValue(linear_to_db(conf[self.id]["volume"]) * 10)
            self.muteButton.setMute(conf[self.id]["mute"])
            self.normal = conf[self.id]["normal_volume"]
            self.normalLabel.setText(str(round(linear_to_db(self.normal), 3))
                                     + " dB")

    def volume_changed(self, value):
        self.volumeLabel.setText(str(value / 10.0) + " dB")

    def pan_changed(self, value):
        if value < 0:
            self.panLabel.setText("Left")
        elif value > 0:
            self.panLabel.setText("Right")
        else:
            self.panLabel.setText("Center")
