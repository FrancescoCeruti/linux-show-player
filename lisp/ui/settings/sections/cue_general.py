##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5 import QtCore
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import *  # @UnusedWildImport

from lisp.ui.settings.section import SettingsSection


class CueGeneral(SettingsSection):

    Name = 'Cue'

    def __init__(self, size, cue=None, parent=None):
        super().__init__(size, cue=cue, parent=parent)

        self.setLayout(QVBoxLayout(self))

        # Groups
        self.groupGroups = QGroupBox(self)
        self.groupGroups.setTitle("Edit groups")
        self.horizontalLayout_5 = QHBoxLayout(self.groupGroups)

        self.editGroups = QLineEdit(self.groupGroups)
        regex = QtCore.QRegExp('(\d+,)*')
        self.editGroups.setValidator(QRegExpValidator(regex))
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.editGroups.setSizePolicy(sizePolicy)
        self.horizontalLayout_5.addWidget(self.editGroups)

        self.groupsEditLabel = QLabel(self.groupGroups)
        self.groupsEditLabel.setText("Modify groups [0,1,2,...,n]")
        self.groupsEditLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontalLayout_5.addWidget(self.groupsEditLabel)

        self.layout().addWidget(self.groupGroups)

    def get_configuration(self):
        conf = {}

        checkable = self.groupGroups.isCheckable()

        if(not (checkable and not self.groupGroups.isChecked())):
            groups_str = self.editGroups.text().split(',')
            if(groups_str[-1] != ''):
                conf['groups'] = [int(groups_str[-1])]
            else:
                conf['groups'] = []
            conf['groups'] += [int(g) for g in groups_str[:-1]]

        return conf

    def enable_check(self, enable):
        self.groupGroups.setCheckable(enable)
        self.groupGroups.setChecked(False)

    def set_configuration(self, conf):
        if('groups' in conf):
            self.editGroups.setText(str(conf['groups'])[1:-1])
