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
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>

from collections import OrderedDict

from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt6.QtWidgets import (
    QDialog,
    QGridLayout,
    QLabel,
    QWidget,
    QTabWidget,
    QTextBrowser,
    QDialogButtonBox,
)

import lisp
from lisp.ui.icons import IconTheme
from lisp.ui.ui_utils import translate


class About(QDialog):
    LICENSE = """
    <p>
    Linux Show Player is free software: you can redistribute it and/or<br />
    modify it under the terms of the GNU General Public License as published by<br />
    the Free Software Foundation, either version 3 of the License, or<br />
    (at your option) any later version.<br />
    <br />
    Linux Show Player is distributed in the hope that it will be useful,<br />
    but WITHOUT ANY WARRANTY; without even the implied warranty of<br />
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the<br />
    GNU General Public License for more details.
    </p>
    """

    DESCRIPTION = QT_TRANSLATE_NOOP(
        "AboutDialog",
        "Linux Show Player is a cue player designed for stage productions.",
    )
    WEB = "https://linux-show-player.org"
    DISCUSS = "https://github.com/FrancescoCeruti/linux-show-player/discussions"
    SOURCE = "https://github.com/FrancescoCeruti/linux-show-player"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.setWindowTitle(translate("About", "About Linux Show Player"))
        self.setMaximumSize(550, 420)
        self.setMinimumSize(550, 420)
        self.resize(550, 420)

        self.setLayout(QGridLayout())

        self.iconLabel = QLabel(self)
        self.iconLabel.setPixmap(
            IconTheme.get("linux-show-player").pixmap(100, 100)
        )
        self.layout().addWidget(self.iconLabel, 0, 0)

        self.shortInfo = QLabel(self)
        self.shortInfo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.shortInfo.setText(
            f"<h2>Linux Show Player   {lisp.__version__}</h2>"
            "Copyright © Francesco Ceruti"
        )
        self.layout().addWidget(self.shortInfo, 0, 1)

        self.layout().addWidget(QWidget(), 1, 0, 1, 2)

        # Information tabs
        self.tabWidget = QTabWidget(self)
        self.layout().addWidget(self.tabWidget, 2, 0, 1, 2)

        self.info = QTextBrowser(self)
        self.info.setOpenExternalLinks(True)
        self.info.setHtml(
            f"""
            <center>
                <br />{translate("AboutDialog", self.DESCRIPTION)}<br /><br />
                <a href="{self.WEB}">{translate("AboutDialog", "Web site")}</a> -
                <a href="{self.DISCUSS}">{translate("AboutDialog", "Discussion")}</a> -
                <a href="{self.SOURCE}">{translate("AboutDialog", "Source code")}</a>
            <center>
            """
        )
        self.tabWidget.addTab(self.info, translate("AboutDialog", "Info"))

        self.license = QTextBrowser(self)
        self.license.setOpenExternalLinks(True)
        self.license.setHtml(self.LICENSE)
        self.tabWidget.addTab(self.license, translate("AboutDialog", "License"))

        self.contributors = QTextBrowser(self)
        self.contributors.setOpenExternalLinks(True)

        self.contributors.setHtml(
            f"""
            <p>
                <u><b>{translate("About", "Authors")}:</b></u><br />
                Francesco Ceruti - <a href="mailto:ceppofrancy@gmail.com">ceppofrancy@gmail.com</a>
            </p>
            <p>
                <u><b>{translate("About", "Contributors")}:</b></u>
                <a href="https://github.com/FrancescoCeruti/linux-show-player/graphs/contributors">GitHub</a>
            </p>
            <p>
                <u><b>{translate("About", "Translators")}:</b></u>
                <a href="https://crowdin.com/project/linux-show-player">Crowdin</a>
            </p>
            """
        )
        self.tabWidget.addTab(
            self.contributors, translate("AboutDialog", "Contributors")
        )

        # Ok button
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.buttons.accepted.connect(self.accept)
        self.layout().addWidget(self.buttons, 3, 1)

        self.layout().setColumnStretch(0, 1)
        self.layout().setColumnStretch(1, 3)

        self.layout().setRowStretch(0, 6)
        self.layout().setRowStretch(1, 1)
        self.layout().setRowStretch(2, 16)
        self.layout().setRowStretch(3, 3)

        self.buttons.setFocus()
