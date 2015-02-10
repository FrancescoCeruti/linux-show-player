##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *  # @UnusedWildImport
from lisp.utils.configuration import config

from lisp.modules.remote.remote import RemoteController, compose_uri
from .peers_discovery_dialog import PeersDiscoveryDialog


class PeersDialog(QDialog):

    def __init__(self, peers):
        super().__init__()

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
        self.setWindowTitle("Manage connected peers")
        self.discoverPeersButton.setText('Discover peers')
        self.addPeerButton.setText("Manually add a peer")
        self.removePeerButton.setText("Remove selected peer")
        self.removeAllButton.setText("Remove all peers")

    def add_peer(self):
        ip, ok = QInputDialog.getText(None, 'Address', 'Peer IP')
        if ok:
            self._add_peer(ip)

    def _add_peer(self, ip):
        port = config['Remote']['BindPort']
        uri = compose_uri(ip, port)

        for peer in self.peers:
            if peer['uri'] == uri:
                QMessageBox.critical(None, 'Error', 'Already connected')
                return

        try:
            peer = {'proxy': RemoteController.connect_to(uri), 'uri': uri}
            self.peers.append(peer)
            self.listWidget.addItem(peer['uri'])
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))

    def discover_peers(self):
        dialog = PeersDiscoveryDialog()
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
