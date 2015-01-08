##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import *  # @UnusedWildImport

from lisp.gst.elements.jack_sink import JackSink
from lisp.ui.settings.section import SettingsSection


class JackSinkSettings(SettingsSection):

    NAME = "Jack Sink"
    ELEMENT = JackSink

    def __init__(self, size, Id, parent=None):
        super().__init__(size, parent)

        self.id = Id

        self.group = QGroupBox(self)
        self.group.setTitle('Jack')
        self.group.setGeometry(0, 0, self.width(), 100)
        self.group.setLayout(QGridLayout())

        self.client = QLineEdit(self.group)
        self.client.setToolTip('The client name of the Jack instance')
        self.client.setText('Linux Show Player')
        self.group.layout().addWidget(self.client, 0, 0)

        self.clientLabel = QLabel('Client name', self.group)
        self.clientLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.group.layout().addWidget(self.clientLabel, 0, 1)

        self.connection = QComboBox(self.group)
        self.connection.setToolTip('Specify how the output ports will be'
                                   'connected')
        self.connection.addItems([JackSink.CONNECT_NONE,
                                  JackSink.CONNECT_AUTO,
                                  JackSink.CONNECT_AUTO_FORCED])
        self.connection.setCurrentIndex(1)
        self.group.layout().addWidget(self.connection, 1, 0)

        self.connLabel = QLabel('Connection mode', self.group)
        self.connLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.group.layout().addWidget(self.connLabel, 1, 1)

    def sizeHint(self):
        return QSize(450, 100)

    def enable_check(self, enable):
        self.group.setCheckable(enable)
        self.group.setChecked(False)

    def set_configuration(self, conf):
        if self.id in conf:
            if 'client-name' in conf[self.id]:
                self.client.setText(conf[self.id]['client-name'])
            if 'connection' in conf[self.id]:
                self.connection.setCurrentText(conf[self.id]['connection'])

    def get_configuration(self):
        if not (self.group.isCheckable() and not self.group.isChecked()):
            return {self.id: {'client-name': self.client.text(),
                              'connection': self.connection.currentText()}}
        else:
            return {}
