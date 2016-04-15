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
import os
import socket
import traceback

from PyQt5.QtWidgets import QMenu, QAction, QMessageBox

from lisp.application import Application
from lisp.core.plugin import Plugin
from lisp.core.signal import Connection
from lisp.ui.mainwindow import MainWindow
from .peers_dialog import PeersDialog


class Synchronizer(Plugin):
    Name = 'Synchronizer'

    def __init__(self):
        self.syncMenu = QMenu('Synchronization')
        self.menu_action = MainWindow().menuTools.addMenu(self.syncMenu)

        self.addPeerAction = QAction('Manage connected peers', MainWindow())
        self.addPeerAction.triggered.connect(self.manage_peers)
        self.syncMenu.addAction(self.addPeerAction)

        self.showIpAction = QAction('Show your IP', MainWindow())
        self.showIpAction.triggered.connect(self.show_ip)
        self.syncMenu.addAction(self.showIpAction)

        self.peers = []
        self.cue_media = {}

    def init(self):
        Application().layout.cue_executed.connect(self.remote_execute,
                                                  mode=Connection.Async)

    def manage_peers(self):
        manager = PeersDialog(self.peers)
        manager.exec_()

    def show_ip(self):
        ip = 'Your IP is:' + os.linesep
        ip += socket.gethostbyname(socket.gethostname())
        QMessageBox.information(MainWindow(), 'Your IP', ip)

    def reset(self):
        self.peers.clear()
        self.cue_media.clear()
        self.syncMenu.clear()

    def remote_execute(self, cue):
        for peer in self.peers:
            try:
                peer['proxy'].execute(cue.index)
            except Exception:
                logging.error('REMOTE: remote control failed')
                logging.debug('REMOTE: ' + traceback.format_exc())
