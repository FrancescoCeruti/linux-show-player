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
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>
import os

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QWidget, QTabWidget, \
    QTextBrowser, QDialogButtonBox

import lisp
from lisp.ui.ui_utils import translate


class About(QDialog):
    LICENSE = '''
    <center>
        Linux Show Player is free software: you can redistribute it and/or
        modify it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.<br />
        <br />
        Linux Show Player is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.
    </center>
    '''

    DESCRIPTION = QT_TRANSLATE_NOOP('AboutDialog',
        'Linux Show Player is a cue-player designed for stage productions.')
    WEB_SITE = 'http://linux-show-player.sourceforge.net'
    USER_GROUP = 'http://groups.google.com/group/linux-show-player---users'
    SOURCE_CODE = 'https://github.com/FrancescoCeruti/linux-show-player'


    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle('About Linux Show Player')
        self.setMaximumSize(500, 420)
        self.setMinimumSize(500, 420)
        self.resize(500, 420)

        self.setLayout(QGridLayout())

        self.iconLabel = QLabel(self)
        self.iconLabel.setPixmap(
            QIcon.fromTheme('linux-show-player').pixmap(100, 100))
        self.layout().addWidget(self.iconLabel, 0, 0)

        self.shortInfo = QLabel(self)
        self.shortInfo.setAlignment(Qt.AlignCenter)
        self.shortInfo.setText('<h2>Linux Show Player   {0}</h2>'
                               'Copyright © Francesco Ceruti'
                               .format(str(lisp.__version__)))
        self.layout().addWidget(self.shortInfo, 0, 1)

        self.layout().addWidget(QWidget(), 1, 0, 1, 2)

        # Information tabs
        self.tabWidget = QTabWidget(self)
        self.layout().addWidget(self.tabWidget, 2, 0, 1, 2)

        self.info = QTextBrowser(self)
        self.info.setOpenExternalLinks(True)
        self.info.setHtml('''
            <center><br />{0}<br /><br />
            <a href="{1}">{2}</a><br />
            <a href="{3}">{4}</a><br />
            <a href="{5}">{6}</a><br /><center>'''.format(
                translate('AboutDialog', self.DESCRIPTION),
                self.WEB_SITE, translate('AboutDialog', 'Web site'),
                self.USER_GROUP, translate('AboutDialog', 'Users  group'),
                self.SOURCE_CODE, translate('AboutDialog', 'Source code'))
        )
        self.tabWidget.addTab(self.info, translate('AboutDialog', 'Info'))

        self.license = QTextBrowser(self)
        self.license.setOpenExternalLinks(True)
        self.license.setHtml(self.LICENSE)
        self.tabWidget.addTab(self.license, translate('AboutDialog', 'License'))

        self.contributors = QTextBrowser(self)
        self.contributors.setOpenExternalLinks(True)
        self.contributors.setHtml('''
            <center><b>{0}</b><br />
            Francesco Ceruti - <a href="mailto:ceppofrancy@gmail.com">ceppofrancy@gmail.com</a>
            <center>'''.format(
                translate('AboutDialog', 'Author:'))
        )
        self.tabWidget.addTab(self.contributors,
                              translate('AboutDialog', 'Contributors'))

        # Ok button
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttons.accepted.connect(self.accept)
        self.layout().addWidget(self.buttons, 3, 1)

        self.layout().setColumnStretch(0, 1)
        self.layout().setColumnStretch(1, 3)

        self.layout().setRowStretch(0, 6)
        self.layout().setRowStretch(1, 1)
        self.layout().setRowStretch(2, 16)
        self.layout().setRowStretch(3, 3)

        self.buttons.setFocus()
