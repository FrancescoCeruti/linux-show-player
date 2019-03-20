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

import logging
import requests
from PyQt5.QtWidgets import QMenu, QAction, QMessageBox

from lisp.core.plugin import Plugin
from lisp.core.signal import Connection
from lisp.core.util import get_lan_ip, compose_url
from lisp.cues.cue import CueAction
from lisp.plugins.network.discovery_dialogs import HostManagementDialog
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class Synchronizer(Plugin):
    Name = "Synchronizer"
    Authors = ("Francesco Ceruti",)
    OptDepends = ("Network",)
    Description = "Keep multiple sessions, on a network, synchronized"

    def __init__(self, app):
        super().__init__(app)
        self.peers = []
        self.app.session_created.connect(self.session_init)

        self.syncMenu = QMenu(translate("Synchronizer", "Synchronization"))
        self.menu_action = self.app.window.menuTools.addMenu(self.syncMenu)

        self.addPeerAction = QAction(
            translate("Synchronizer", "Manage connected peers"), self.app.window
        )
        self.addPeerAction.triggered.connect(self.manage_peers)
        self.syncMenu.addAction(self.addPeerAction)

        self.showIpAction = QAction(
            translate("Synchronizer", "Show your IP"), self.app.window
        )
        self.showIpAction.triggered.connect(self.show_ip)
        self.syncMenu.addAction(self.showIpAction)

    def session_init(self):
        self.app.layout.cue_executed.connect(
            self._cue_executes, mode=Connection.Async
        )
        self.app.layout.all_executed.connect(
            self._all_executed, mode=Connection.Async
        )

    def manage_peers(self):
        manager = HostManagementDialog(
            self.peers,
            Synchronizer.Config["discovery.port"],
            Synchronizer.Config["discovery.magic"],
            parent=self.app.window,
        )
        manager.exec()

        self.peers = manager.hosts()

    def show_ip(self):
        ip = translate("Synchronizer", "Your IP is:") + " " + str(get_lan_ip())
        QMessageBox.information(self.app.window, " ", ip)

    def _url(self, host, path):
        return compose_url(
            Synchronizer.Config["protocol"],
            host,
            Synchronizer.Config["port"],
            path,
        )

    def _cue_executes(self, cue):
        for peer in self.peers:
            requests.post(
                self._url(peer, "/cues/{}/action".format(cue.id)),
                json={"action": CueAction.Default.value},
            )

    def _all_executed(self, action):
        for peer in self.peers:
            requests.post(
                self._url(peer, "/layout/action"), json={"action": action.value}
            )
