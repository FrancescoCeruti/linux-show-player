# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QGroupBox, QGridLayout, QLineEdit, QLabel, \
    QComboBox

from lisp.backends.gst.elements.jack_sink import JackSink
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
