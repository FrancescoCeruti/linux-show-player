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
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QGroupBox,
    QHBoxLayout,
    QTextEdit,
    QSpinBox,
    QLabel,
    QLineEdit,
)

from lisp.ui.settings.pages import SettingsPage
from lisp.ui.widgets import QColorButton
from lisp.ui.ui_utils import translate


class Appearance(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Appearance")

    def __init__(self, **kwargs):
        super().__init__()
        self.setLayout(QVBoxLayout())

        # Name
        self.cueNameGroup = QGroupBox(self)
        self.cueNameGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.cueNameGroup)

        self.cueNameEdit = QLineEdit(self.cueNameGroup)
        self.cueNameGroup.layout().addWidget(self.cueNameEdit)

        # Description
        self.cueDescriptionGroup = QGroupBox(self)
        self.cueDescriptionGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.cueDescriptionGroup)

        self.cueDescriptionEdit = QTextEdit(self.cueNameGroup)
        self.cueDescriptionGroup.layout().addWidget(self.cueDescriptionEdit)

        # Font
        self.fontSizeGroup = QGroupBox(self)
        self.fontSizeGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.fontSizeGroup)

        self.fontSizeSpin = QSpinBox(self.fontSizeGroup)
        self.fontSizeSpin.setValue(QLabel().fontInfo().pointSize())
        self.fontSizeGroup.layout().addWidget(self.fontSizeSpin)

        # Color
        self.colorGroup = QGroupBox(self)
        self.colorGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.colorGroup)

        self.colorBButton = QColorButton(self.colorGroup)
        self.colorFButton = QColorButton(self.colorGroup)

        self.colorGroup.layout().addWidget(self.colorBButton)
        self.colorGroup.layout().addWidget(self.colorFButton)

        # Warning
        self.warning = QLabel(self)
        self.warning.setText(
            translate(
                "CueAppearanceSettings", "The appearance depends on the layout"
            )
        )
        self.warning.setAlignment(Qt.AlignCenter)
        self.warning.setStyleSheet("color: #FFA500; font-weight: bold")
        self.layout().addWidget(self.warning)

        self.retranslateUi()

    def retranslateUi(self):
        self.cueNameGroup.setTitle(
            translate("CueAppearanceSettings", "Cue name")
        )
        self.cueNameEdit.setText(translate("CueAppearanceSettings", "NoName"))
        self.cueDescriptionGroup.setTitle(
            translate("CueAppearanceSettings", "Description/Note")
        )
        self.fontSizeGroup.setTitle(
            translate("CueAppearanceSettings", "Set Font Size")
        )
        self.colorGroup.setTitle(translate("CueAppearanceSettings", "Color"))
        self.colorBButton.setText(
            translate("CueAppearanceSettings", "Select background color")
        )
        self.colorFButton.setText(
            translate("CueAppearanceSettings", "Select font color")
        )

    def enableCheck(self, enabled):
        self.cueNameGroup.setCheckable(enabled)
        self.cueNameGroup.setChecked(False)

        self.cueDescriptionGroup.setChecked(enabled)
        self.cueDescriptionGroup.setChecked(False)

        self.fontSizeGroup.setCheckable(enabled)
        self.fontSizeGroup.setChecked(False)

        self.colorGroup.setCheckable(enabled)
        self.colorGroup.setChecked(False)

    def getSettings(self):
        settings = {}
        style = {}
        checkable = self.cueNameGroup.isCheckable()

        if not (checkable and not self.cueNameGroup.isChecked()):
            settings["name"] = self.cueNameEdit.text()
        if not (checkable and not self.cueDescriptionGroup.isChecked()):
            settings["description"] = self.cueDescriptionEdit.toPlainText()
        if not (checkable and not self.colorGroup.isChecked()):
            if self.colorBButton.color() is not None:
                style["background"] = self.colorBButton.color()
            if self.colorFButton.color() is not None:
                style["color"] = self.colorFButton.color()
        if not (checkable and not self.fontSizeGroup.isChecked()):
            style["font-size"] = str(self.fontSizeSpin.value()) + "pt"

        if style:
            settings["stylesheet"] = dict_to_css(style)

        return settings

    def loadSettings(self, settings):
        if "name" in settings:
            self.cueNameEdit.setText(settings["name"])
        if "description" in settings:
            self.cueDescriptionEdit.setText(settings["description"])
        if "stylesheet" in settings:
            settings = css_to_dict(settings["stylesheet"])
            if "background" in settings:
                self.colorBButton.setColor(settings["background"])
            if "color" in settings:
                self.colorFButton.setColor(settings["color"])
            if "font-size" in settings:
                # [:-2] for removing "pt"
                self.fontSizeSpin.setValue(int(settings["font-size"][:-2]))


def css_to_dict(css):
    dict = {}
    css = css.strip()

    for attribute in css.split(";"):
        try:
            name, value = attribute.split(":")
            dict[name.strip()] = value.strip()
        except Exception:
            pass

    return dict


def dict_to_css(css_dict):
    css = ""
    for name in css_dict:
        css += name + ":" + str(css_dict[name]) + ";"

    return css
