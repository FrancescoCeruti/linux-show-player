# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QListWidget,
    QDialogButtonBox,
    QDialog,
    QHBoxLayout,
    QPushButton,
    QInputDialog,
    QListWidgetItem,
)

from lisp.core.signal import Connection
from lisp.plugins.network.discovery import Discoverer
from lisp.ui.ui_utils import translate
from lisp.ui.widgets.qprogresswheel import QProgressWheel


class HostDiscoveryDialog(QDialog):
    def __init__(self, port, magic, **kwargs):
        super().__init__(**kwargs)
        self.setWindowModality(Qt.WindowModal)
        self.setLayout(QVBoxLayout())
        self.setMaximumSize(300, 200)
        self.setMinimumSize(300, 200)
        self.resize(300, 200)

        self.listWidget = QListWidget(self)
        self.listWidget.setAlternatingRowColors(True)
        self.listWidget.setSelectionMode(self.listWidget.MultiSelection)
        self.layout().addWidget(self.listWidget)

        self.progressWheel = QProgressWheel()

        self.progressItem = QListWidgetItem()
        self.progressItem.setFlags(Qt.NoItemFlags)
        self.progressItem.setSizeHint(QSize(30, 30))
        self.listWidget.addItem(self.progressItem)
        self.listWidget.setItemWidget(self.progressItem, self.progressWheel)

        self.dialogButton = QDialogButtonBox(self)
        self.dialogButton.setStandardButtons(self.dialogButton.Ok)
        self.dialogButton.accepted.connect(self.accept)
        self.layout().addWidget(self.dialogButton)

        self.retranslateUi()

        self._discoverer = Discoverer(port, magic, max_attempts=10)
        self._discoverer.discovered.connect(
            self._host_discovered, Connection.QtQueued
        )
        self._discoverer.ended.connect(self._search_ended, Connection.QtQueued)

    def retranslateUi(self):
        self.setWindowTitle(translate("NetworkDiscovery", "Host discovery"))

    def accept(self):
        self._discoverer.stop()
        return super().accept()

    def reject(self):
        self._discoverer.stop()
        return super().reject()

    def exec_(self):
        self.layout().activate()
        self.progressWheel.startAnimation()

        self._discoverer.start()
        return super().exec()

    def hosts(self):
        return [item.text() for item in self.listWidget.selectedItems()]

    def _host_discovered(self, host):
        self.listWidget.insertItem(self.listWidget.count() - 1, host)

    def _search_ended(self):
        self.listWidget.takeItem(self.listWidget.count() - 1)
        self.progressWheel.stopAnimation()


class HostManagementDialog(QDialog):
    def __init__(self, hosts, discovery_port, discovery_magic, **kwargs):
        super().__init__(**kwargs)
        self.discovery_port = discovery_port
        self.discovery_magic = discovery_magic

        self.setWindowModality(Qt.WindowModal)
        self.setLayout(QHBoxLayout())
        self.setMaximumSize(500, 200)
        self.setMinimumSize(500, 200)
        self.resize(500, 200)

        self.listWidget = QListWidget(self)
        self.listWidget.setAlternatingRowColors(True)
        self.listWidget.addItems(hosts)
        self.layout().addWidget(self.listWidget)

        self.buttonsLayout = QVBoxLayout()
        self.layout().addLayout(self.buttonsLayout)

        self.discoverHostsButton = QPushButton(self)
        self.discoverHostsButton.clicked.connect(self.discoverHosts)
        self.buttonsLayout.addWidget(self.discoverHostsButton)

        self.addHostButton = QPushButton(self)
        self.addHostButton.clicked.connect(self.addHostDialog)
        self.buttonsLayout.addWidget(self.addHostButton)

        self.removeHostButton = QPushButton(self)
        self.removeHostButton.clicked.connect(self.removeSelectedHosts)
        self.buttonsLayout.addWidget(self.removeHostButton)

        self.removeAllButton = QPushButton(self)
        self.removeAllButton.clicked.connect(self.removeAllHosts)
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
        self.setWindowTitle(translate("NetworkDiscovery", "Manage hosts"))
        self.discoverHostsButton.setText(
            translate("NetworkDiscovery", "Discover hosts")
        )
        self.addHostButton.setText(
            translate("NetworkDiscovery", "Manually add a host")
        )
        self.removeHostButton.setText(
            translate("NetworkDiscovery", "Remove selected host")
        )
        self.removeAllButton.setText(
            translate("NetworkDiscovery", "Remove all host")
        )

    def addHostDialog(self):
        host, ok = QInputDialog.getText(
            self,
            translate("NetworkDiscovery", "Address"),
            translate("NetworkDiscovery", "Host IP"),
        )

        if ok:
            self.addHost(host)

    def addHost(self, host):
        if not self.listWidget.findItems(host, Qt.MatchExactly):
            self.listWidget.addItem(host)

    def discoverHosts(self):
        dialog = HostDiscoveryDialog(
            self.discovery_port, self.discovery_magic, parent=self
        )

        if dialog.exec() == dialog.Accepted:
            for host in dialog.hosts():
                self.addHost(host)

    def removeSelectedHosts(self):
        for index in self.listWidget.selectedIndexes():
            self.listWidget.takeItem(index)

    def removeAllHosts(self):
        self.listWidget.clear()

    def hosts(self):
        hosts = []
        for index in range(self.listWidget.count()):
            hosts.append(self.listWidget.item(index).text())

        return hosts
