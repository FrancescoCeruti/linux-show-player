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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QListWidget, QDialogButtonBox, \
    QListWidgetItem, QDialog

from lisp.core.signal import Connection
from lisp.modules.remote.discovery import Discoverer
from lisp.ui.ui_utils import translate


class PeersDiscoveryDialog(QDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setWindowModality(Qt.ApplicationModal)
        self.setLayout(QVBoxLayout())
        self.setMaximumSize(300, 200)
        self.setMinimumSize(300, 200)
        self.resize(300, 200)

        self.listWidget = QListWidget(self)
        self.listWidget.setAlternatingRowColors(True)
        self.listWidget.setSelectionMode(self.listWidget.MultiSelection)
        self.layout().addWidget(self.listWidget)

        self.dialogButton = QDialogButtonBox(self)
        self.dialogButton.setStandardButtons(self.dialogButton.Ok)
        self.dialogButton.accepted.connect(self.accept)
        self.layout().addWidget(self.dialogButton)

        self.retranslateUi()

        self._discoverer = Discoverer()
        self._discoverer.discovered.connect(self._new_peer, Connection.QtQueued)

    def retranslateUi(self):
        self.setWindowTitle(translate('Synchronizer', 'Discovering peers ...'))

    def accept(self):
        self._discoverer.stop()
        return super().accept()

    def reject(self):
        self._discoverer.stop()
        return super().reject()

    def exec_(self):
        self._discoverer.start()
        return super().exec_()

    def get_peers(self):
        return [item.address for item in self.listWidget.selectedItems()]

    def _new_peer(self, peer):
        item = QListWidgetItem(peer[1] + ' - ' + peer[0])
        item.address = peer[0]

        self.listWidget.addItem(item)
