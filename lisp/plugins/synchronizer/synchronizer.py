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

import logging
import traceback

from PyQt5.QtWidgets import QMenu, QAction, QMessageBox

from lisp.application import Application
from lisp.core.plugin import Plugin
from lisp.core.signal import Connection
from lisp.core.util import get_lan_ip
from lisp.ui.mainwindow import MainWindow
from lisp.ui.ui_utils import translate
from .peers_dialog import PeersDialog


class Synchronizer(Plugin):

    Name = 'Synchronizer'
    Authors = ('Francesco Ceruti', )
    Depends = ('Remote', )
    Description = 'Keep multiple sessions, on a network, synchronized'

    def __init__(self, app):
        super().__init__(app)

        self.syncMenu = QMenu(translate('Synchronizer', 'Synchronization'))
        self.menu_action = self.app.window.menuTools.addMenu(self.syncMenu)

        self.addPeerAction = QAction(
            translate('Synchronizer', 'Manage connected peers'), self.app.window)
        self.addPeerAction.triggered.connect(self.manage_peers)
        self.syncMenu.addAction(self.addPeerAction)

        self.showIpAction = QAction(
            translate('Synchronizer', 'Show your IP'), self.app.window)
        self.showIpAction.triggered.connect(self.show_ip)
        self.syncMenu.addAction(self.showIpAction)

        self.peers = []
        self.cue_media = {}

        self.app.session_created.connect(self.session_init)
        self.app.session_before_finalize.connect(self.session_reset)

    def session_init(self):
        self.app.layout.cue_executed.connect(
            self.remote_execute, mode=Connection.Async)

    def session_reset(self):
        self.peers.clear()
        self.cue_media.clear()

    def manage_peers(self):
        manager = PeersDialog(
            self.peers, Synchronizer.Config, parent=self.app.window)
        manager.exec_()

    def show_ip(self):
        ip = translate('Synchronizer', 'Your IP is:') + ' ' + str(get_lan_ip())
        QMessageBox.information(self.app.window, ' ', ip)

    def remote_execute(self, cue):
        for peer in self.peers:
            try:
                peer['proxy'].execute(cue.index)
            except Exception:
                logging.error('REMOTE: remote control failed')
                logging.debug('REMOTE: ' + traceback.format_exc())
