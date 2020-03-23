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
    QGridLayout,
    QLabel,
)

from lisp.core.signal import Connection
from lisp.plugins.network.discovery import Discoverer
from lisp.ui.ui_utils import translate
from lisp.ui.widgets.qwaitingspinner import QWaitingSpinner


class HostDiscoveryDialog(QDialog):
    def __init__(self, port, magic, **kwargs):
        super().__init__(**kwargs)
        self.setWindowModality(Qt.WindowModal)
        self.setLayout(QGridLayout())
        self.setMinimumSize(300, 200)
        self.resize(500, 200)

        self.hintLabel = QLabel(self)
        self.layout().addWidget(self.hintLabel, 0, 0, 1, 2)

        self.listWidget = QListWidget(self)
        self.listWidget.setAlternatingRowColors(True)
        self.listWidget.setSelectionMode(self.listWidget.MultiSelection)
        self.layout().addWidget(self.listWidget, 1, 0, 1, 2)

        self.progressSpinner = QWaitingSpinner(
            parent=self, centerOnParent=False
        )
        self.progressSpinner.setInnerRadius(8)
        self.progressSpinner.setLineWidth(4)
        self.progressSpinner.setLineLength(4)
        self.layout().addWidget(self.progressSpinner, 2, 0)

        self.dialogButton = QDialogButtonBox(self)
        self.dialogButton.setStandardButtons(self.dialogButton.Ok)
        self.dialogButton.accepted.connect(self.accept)
        self.layout().addWidget(self.dialogButton, 2, 1)

        self.retranslateUi()

        self._discoverer = Discoverer(port, magic, max_attempts=10)
        self._discoverer.discovered.connect(
            self._host_discovered, Connection.QtQueued
        )
        self._discoverer.ended.connect(self._search_ended, Connection.QtQueued)

    def retranslateUi(self):
        self.hintLabel.setText(
            translate("NetworkDiscovery", "Select the hosts you want to add")
        )
        self.setWindowTitle(translate("NetworkDiscovery", "Host discovery"))

    def accept(self):
        self._discoverer.stop()
        return super().accept()

    def reject(self):
        self._discoverer.stop()
        return super().reject()

    def exec(self):
        self.progressSpinner.start()
        self._discoverer.start()

        return super().exec()

    def hosts(self):
        return [
            (item.data(Qt.UserRole), item.text())
            for item in self.listWidget.selectedItems()
        ]

    def _host_discovered(self, host, fqdn):
        if fqdn != host:
            item_text = "{} - {}".format(fqdn, host)
        else:
            item_text = host

        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, host)
        item.setSizeHint(QSize(100, 30))
        self.listWidget.addItem(item)

    def _search_ended(self):
        self.progressSpinner.stop()


class HostManagementDialog(QDialog):
    def __init__(self, hosts, discovery_port, discovery_magic, **kwargs):
        super().__init__(**kwargs)
        self.discovery_port = discovery_port
        self.discovery_magic = discovery_magic

        self.setWindowModality(Qt.WindowModal)
        self.setLayout(QHBoxLayout())
        self.setMinimumSize(500, 200)
        self.resize(500, 200)

        self.listWidget = QListWidget(self)
        self.listWidget.setAlternatingRowColors(True)
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
        self.addHosts(hosts)

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

        if host and ok:
            self.addHost(host, host)

    def addHosts(self, hosts):
        for host in hosts:
            if isinstance(host, str):
                self.addHost(host, host)
            else:
                self.addHost(*host)

    def addHost(self, hostname, display_name):
        if not self.listWidget.findItems(hostname, Qt.MatchEndsWith):
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, hostname)
            item.setSizeHint(QSize(100, 30))
            self.listWidget.addItem(item)

    def discoverHosts(self):
        dialog = HostDiscoveryDialog(
            self.discovery_port, self.discovery_magic, parent=self
        )

        if dialog.exec() == dialog.Accepted:
            for hostname, display_name in dialog.hosts():
                self.addHost(hostname, display_name)

    def removeSelectedHosts(self):
        for index in self.listWidget.selectedIndexes():
            self.listWidget.takeItem(index)

    def removeAllHosts(self):
        self.listWidget.clear()

    def hosts(self):
        hosts = []
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            hosts.append((item.data(Qt.UserRole), item.text()))

        return hosts
