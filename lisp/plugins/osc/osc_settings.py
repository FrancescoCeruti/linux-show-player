# This file is part of Linux Show Player
#
# Copyright 2024 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2016 Thomas Achtner <info@offtools.de>
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

from PyQt6.QtCore import QT_TRANSLATE_NOOP, Qt
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QSpinBox,
    QLineEdit,
)

from lisp.core.util import get_lan_ip
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class OscSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "OSC settings")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        self.inwardsGroupBox = QGroupBox(self)
        self.inwardsGroupBox.setLayout(QGridLayout())
        self.layout().addWidget(self.inwardsGroupBox)

        self.inwardsLabel = QLabel()
        self.inwardsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.inwardsLabel.font()
        font.setPointSizeF(font.pointSizeF() * 0.9)
        self.inwardsLabel.setFont(font)
        self.inwardsGroupBox.layout().addWidget(self.inwardsLabel, 0, 0, 1, 2)

        self.localaddrLabel = QLabel()
        self.localaddrValue = QLabel(get_lan_ip())
        self.inwardsGroupBox.layout().addWidget(self.localaddrLabel, 1, 0)
        self.inwardsGroupBox.layout().addWidget(self.localaddrValue, 1, 1)

        self.inportLabel = QLabel()
        self.inportBox = QSpinBox()
        self.inportBox.setMinimum(1000)
        self.inportBox.setMaximum(99999)
        self.inwardsGroupBox.layout().addWidget(self.inportLabel, 2, 0)
        self.inwardsGroupBox.layout().addWidget(self.inportBox, 2, 1)

        self.outwardsGroupBox = QGroupBox(self)
        self.outwardsGroupBox.setLayout(QGridLayout())
        self.layout().addWidget(self.outwardsGroupBox)

        self.outwardsLabel = QLabel()
        self.outwardsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.outwardsLabel.setFont(font)
        self.outwardsGroupBox.layout().addWidget(self.outwardsLabel, 0, 0, 1, 2)

        self.hostnameLabel = QLabel()
        self.hostnameEdit = QLineEdit()
        self.hostnameEdit.setText("localhost")
        self.hostnameEdit.setMaximumWidth(200)
        self.outwardsGroupBox.layout().addWidget(self.hostnameLabel, 1, 0)
        self.outwardsGroupBox.layout().addWidget(self.hostnameEdit, 1, 1)

        self.outportLabel = QLabel()
        self.outportBox = QSpinBox()
        self.outportBox.setMinimum(1000)
        self.outportBox.setMaximum(99999)
        self.outwardsGroupBox.layout().addWidget(self.outportLabel, 2, 0)
        self.outwardsGroupBox.layout().addWidget(self.outportBox, 2, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.inwardsGroupBox.setTitle(
            translate("OscSettings", "OSC Input Settings")
        )
        self.inwardsLabel.setText(
            translate(
                "OscSettings",
                "Linux Show Player will pick up OSC messages sent via UDP to:",
            )
        )
        self.localaddrLabel.setText(translate("OscSettings", "Address:"))
        self.inportLabel.setText(translate("OscSettings", "Port:"))

        self.outwardsGroupBox.setTitle(
            translate("OscSettings", "OSC Output Settings")
        )
        self.outwardsLabel.setText(
            translate(
                "OscSettings", "Messages from OSC Cues will be sent via UDP to:"
            )
        )
        self.hostnameLabel.setText(translate("OscSettings", "Address:"))
        self.outportLabel.setText(translate("OscSettings", "Port:"))

    def getSettings(self):
        return {
            "inPort": self.inportBox.value(),
            "outPort": self.outportBox.value(),
            "hostname": self.hostnameEdit.text(),
        }

    def loadSettings(self, settings):
        self.inportBox.setValue(settings["inPort"])
        self.outportBox.setValue(settings["outPort"])
        self.hostnameEdit.setText(settings["hostname"])
