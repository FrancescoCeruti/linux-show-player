##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox, \
    QListWidgetItem

from lisp.modules.remote.discovery import Discoverer


class PeersDiscoveryDialog(QDialog):

    def __init__(self):
        super().__init__()

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
        self._discoverer.discovered.connect(self._new_peer)

    def retranslateUi(self):
        self.setWindowTitle("Discovering peers ...")

    def accept(self, *args, **kwargs):
        self._discoverer.stop()
        return QDialog.accept(self, *args, **kwargs)

    def exec_(self, *args, **kwargs):
        self._discoverer.start()
        return QDialog.exec_(self, *args, **kwargs)

    def get_peers(self):
        return [item.adders for item in self.listWidget.selectedItems()]

    def _new_peer(self, peer):
        item = QListWidgetItem(peer[1] + ' at ' + peer[0])
        item.adders = peer[0]

        self.listWidget.addItem(item)
