##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of Linux Show Player.
##########################################

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *  # @UnusedWildImport
import lisp
from lisp.utils import util


class About(QDialog):

    ICON = util.file_path(__file__, "icon.png")

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle('About Linux Show Player')
        self.setMaximumSize(500, 410)
        self.setMinimumSize(500, 410)
        self.resize(500, 410)

        self.setLayout(QGridLayout())

        self.icon = QLabel(self)
        self.icon.setPixmap(QPixmap(self.ICON).scaled(100, 100,
                            transformMode=Qt.SmoothTransformation))
        self.layout().addWidget(self.icon, 0, 0)

        self.shortInfo = QLabel(self)
        self.shortInfo.setAlignment(Qt.AlignCenter)
        self.shortInfo.setText('<h2>Linux Show Player   ' +
                               str(lisp.__version__) + '</h2>'
                               'Copyright © Francesco Ceruti')
        self.layout().addWidget(self.shortInfo, 0, 1)

        self.layout().addWidget(QWidget(), 1, 0, 1, 2)

        # Informations tabs
        self.tabWidget = QTabWidget(self)
        self.layout().addWidget(self.tabWidget, 2, 0, 1, 2)

        self.info = QTextBrowser(self)
        self.info.setOpenExternalLinks(True)
        self.info.setHtml(self.INFO)
        self.tabWidget.addTab(self.info, 'Info')

        self.license = QTextBrowser(self)
        self.license.setOpenExternalLinks(True)
        self.license.setHtml(self.LICENSE)
        self.tabWidget.addTab(self.license, 'License')

        self.contributors = QTextBrowser(self)
        self.contributors.setOpenExternalLinks(True)
        self.contributors.setHtml(self.CONTRIBUTORS)
        self.tabWidget.addTab(self.contributors, 'Contributors')

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

    LICENSE = '''
<center>
    <b>Linux Show Player</b><br />
    Copyright © 2012-2014 Francesco Ceruti<br />
    <br />
    Linux Show Player is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.<br />
    <br />
    Linux Show Player is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
</center>'''

    INFO = '''
<center><br />
    Linux Show Player is a cue-player designed for stage productions.<br \>
</center>
<center><br />
    Web site: <a href="http://linux-show-player.sourceforge.net">linux-show-player.sourceforge.net</a><br \>
    User group: <a href="http://groups.google.com/group/linux-show-player---users">groups.google.com</a><br \>
    Source code: <a href="https://github.com/FrancescoCeruti/linux-show-player">GitHub</a>
</center>'''

    CONTRIBUTORS = '''
<center>
    <b>Author:</b><br />
    Francesco Ceruti - <a href="mailto:ceppofrancy@gmail.com">ceppofrancy@gmail.com</a><br \><br />
    <b>Contributors:</b><br />
    Marco Asa
</center>
'''
