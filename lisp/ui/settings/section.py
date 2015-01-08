##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QWidget


class SettingsSection(QWidget):

    Name = 'Section'

    def __init__(self, size=QRect(), cue=None, parent=None):
        super().__init__(parent)
        self.resize(self.sizeHint() if size is None else size)

        self.cue = cue

    def enable_check(self, enable):
        ''' Enable option check '''

    def get_configuration(self):
        ''' Return the current settings '''
        return {}

    def set_configuration(self, conf):
        ''' Load the settings '''
