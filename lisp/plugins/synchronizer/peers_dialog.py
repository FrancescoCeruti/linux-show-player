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
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QListWidget, QVBoxLayout, \
    QPushButton, QDialogButtonBox, QInputDialog, QMessageBox

from lisp.core.configuration import config
from lisp.core.util import compose_http_url
from lisp.modules.remote.remote import RemoteController
from lisp.ui import elogging
from lisp.ui.ui_utils import translate
from .peers_discovery_dialog import PeersDiscoveryDialog


class PeersDialog(QDialog):
    def __init__(self, peers, **kwargs):
        super().__init__(**kwargs)
        self.peers = peers

        self.setWindowModality(Qt.ApplicationModal)
        self.setMaximumSize(500, 200)
        self.setMinimumSize(500, 200)
        self.resize(500, 200)

        self.setLayout(QHBoxLayout())

        self.listWidget = QListWidget(self)
        self.listWidget.setAlternatingRowColors(True)
        self.layout().addWidget(self.listWidget)

        for peer in self.peers:
            self.listWidget.addItem(peer['uri'])

        self.buttonsLayout = QVBoxLayout()
        self.layout().addLayout(self.buttonsLayout)

        self.discoverPeersButton = QPushButton(self)
        self.addPeerButton = QPushButton(self)
        self.removePeerButton = QPushButton(self)
        self.removeAllButton = QPushButton(self)

        self.discoverPeersButton.clicked.connect(self.discover_peers)
        self.addPeerButton.clicked.connect(self.add_peer)
        self.removePeerButton.clicked.connect(self.remove_peer)
        self.removeAllButton.clicked.connect(self.remove_all)

        self.buttonsLayout.addWidget(self.discoverPeersButton)
        self.buttonsLayout.addWidget(self.addPeerButton)
        self.buttonsLayout.addWidget(self.removePeerButton)
        self.buttonsLayout.addWidget(self.removeAllButton)
        self.buttonsLayout.addSpacing(70)

        self.dialogButton = QDialogButtonBox(self)
        self.dialogButton.setStandardButtons(self.dialogButton.Ok)
        self.dialogButton.accepted.connect(self.accept)
        self.buttonsLayout.addWidget(self.dialogButton)

        self.layout().setStretch(0, 2)
        self.layout().setStretch(1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(
            translate('SyncPeerDialog', 'Manage connected peers'))
        self.discoverPeersButton.setText(
            translate('SyncPeerDialog', 'Discover peers'))
        self.addPeerButton.setText(
            translate('SyncPeerDialog', 'Manually add a peer'))
        self.removePeerButton.setText(
            translate('SyncPeerDialog', 'Remove selected peer'))
        self.removeAllButton.setText(
            translate('SyncPeerDialog', 'Remove all peers'))

    def add_peer(self):
        ip, ok = QInputDialog.getText(self,
                                      translate('SyncPeerDialog', 'Address'),
                                      translate('SyncPeerDialog', 'Peer IP'))
        if ok:
            self._add_peer(ip)

    def _add_peer(self, ip):
        port = config['Remote']['BindPort']
        uri = compose_http_url(ip, port)

        for peer in self.peers:
            if peer['uri'] == uri:
                QMessageBox.critical(self,
                                     translate('SyncPeerDialog', 'Error'),
                                     translate('SyncPeerDialog',
                                               'Already connected'))
                return

        try:
            peer = {'proxy': RemoteController.connect_to(uri), 'uri': uri}
            self.peers.append(peer)
            self.listWidget.addItem(peer['uri'])
        except Exception as e:
            elogging.exception(translate('SyncPeerDialog', 'Cannot add peer'),
                               str(e))

    def discover_peers(self):
        dialog = PeersDiscoveryDialog(parent=self)
        if dialog.exec_() == dialog.Accepted:
            for peer in dialog.get_peers():
                self._add_peer(peer)

    def remove_peer(self):
        if len(self.listWidget.selectedIndexes()) != 0:
            self.peers.pop(self.current_index())
            self.listWidget.takeItem(self.current_index())

    def remove_all(self):
        self.peers.clear()
        self.listWidget.clear()

    def current_index(self):
        return self.listWidget.selectedIndexes()[0].row()
