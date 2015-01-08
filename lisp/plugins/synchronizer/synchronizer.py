##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import os
import socket

from PyQt5.QtWidgets import QMenu, QAction, QMessageBox
from lisp import modules
from lisp.core.plugin import Plugin

from lisp.application import Application
from lisp.cues.media_cue import MediaCue

from .peers_dialog import PeersDialog


class Synchronizer(Plugin):

    Name = 'Synchronizer'

    def __init__(self):
        if not modules.check_module('remote'):
            raise Exception('The "remote" module is not running')

        self.app = Application()
        self.syncMenu = QMenu('Synchronization')
        self.menu_action = self.app.mainWindow.menuTools.addMenu(self.syncMenu)

        self.addPeerAction = QAction('Manage connected peers',
                                     self.app.mainWindow)
        self.addPeerAction.triggered.connect(self.manage_peers)
        self.syncMenu.addAction(self.addPeerAction)

        self.showIpAction = QAction('Show your IP',
                                    self.app.mainWindow)
        self.showIpAction.triggered.connect(self.show_ip)
        self.syncMenu.addAction(self.showIpAction)

        self.peers = []
        self.cue_media = {}

        self.app.layout.cue_added.connect(self._connect_cue)
        self.app.layout.cue_removed.connect(self._disconnect_cue)

    def manage_peers(self):
        manager = PeersDialog(self.peers)
        manager.exec_()

    def show_ip(self):
        ip = 'Your IP is:' + os.linesep
        ip += socket.gethostbyname(socket.gethostname())
        QMessageBox.information(None, 'Your IP', ip)

    def reset(self):
        self.peers = []
        self.cue_media = {}

        self.app.layout.cue_added.disconnect(self._connect_cue)
        self.app.layout.cue_removed.disconnect(self._disconnect_cue)

        self.syncMenu.clear()
        self.app.mainWindow.menuTools.removeAction(self.menu_action)

    def _connect_cue(self, cue):
        cue.executed.connect(self.remote_trigger)

        if isinstance(cue, MediaCue):
            self.cue_media[cue.media] = cue

            cue.media.on_play.connect(self.remote_play)
            cue.media.on_stop.connect(self.remote_stop)
            cue.media.on_pause.connect(self.remote_pause)
            cue.media.sought.connect(self.remote_seek)

    def _disconnect_cue(self, cue):
        cue.executed.disconnect(self.remote_trigger)

        if isinstance(cue, MediaCue):
            self.cue_media.pop(cue.media)

            cue.media.on_play.disconnect(self.remote_play)
            cue.media.on_stop.disconnect(self.remote_stop)
            cue.media.on_pause.disconnect(self.remote_pause)
            cue.media.sought.disconnect(self.remote_seek)

    def remote_play(self, media):
        for peer in self.peers:
            try:
                peer['proxy'].play(self.cue_media[media]['index'])
            except Exception:
                self.peers.remove(peer)

    def remote_pause(self, media):
        for peer in self.peers:
            try:
                peer['proxy'].pause(self.cue_media[media]['index'])
            except Exception:
                self.peers.remove(peer)

    def remote_stop(self, media):
        for peer in self.peers:
            try:
                peer['proxy'].stop(self.cue_media[media]['index'])
            except Exception:
                self.peers.remove(peer)

    def remote_seek(self, media, position):
        for peer in self.peers:
            try:
                peer['proxy'].seek(self.cue_media[media]['index'], position)
            except Exception:
                self.peers.remove(peer)

    def remote_trigger(self, cue):
        for peer in self.peers:
            try:
                peer.execute(cue['index'])
            except Exception:
                self.peers.remove(peer)
