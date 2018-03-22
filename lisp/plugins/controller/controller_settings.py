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

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.plugins.controller import protocols
from lisp.ui.settings.pages import TabsMultiSettingsPage, CuePageMixin


class ControllerSettings(TabsMultiSettingsPage, CuePageMixin):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'Cue Control')

    def __init__(self, cue_type, **kwargs):
        super().__init__(cue_type=cue_type, **kwargs)

        for page in protocols.ProtocolsSettingsPages:
            self.addPage(page(cue_type, parent=self))

    def getSettings(self):
        return {'controller': super().getSettings()}

    def loadSettings(self, settings):
        super().loadSettings(settings.get('controller', {}))
