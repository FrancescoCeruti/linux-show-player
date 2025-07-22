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

import glob
import os
from PyQt5.QtCore import Qt, QCoreApplication, QEvent, QSize, QT_TRANSLATE_NOOP
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QGroupBox,
    QHBoxLayout,
    QTextEdit,
    QSpinBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QDialog,
    QGridLayout,
    QDialogButtonBox,
    QToolButton,
    QApplication,
)

from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate, css_to_dict, dict_to_css
from lisp.ui.widgets import ColorButton
from lisp.ui.icons import IconTheme
from lisp import ICON_THEMES_DIR


class Appearance(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Appearance")
    iconName = "music"

    def __init__(self, **kwargs):
        super().__init__()
        self.setLayout(QVBoxLayout())

        # Name
        self.cueNameGroup = QGroupBox(self)
        self.cueNameGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.cueNameGroup)

        self.cueNameEdit = QLineEdit(self.cueNameGroup)
        self.cueNameGroup.layout().addWidget(self.cueNameEdit)

        # Icon
        self.iconSelectorDialog = IconSelectorDialog(self, self.selectIcon)
        self.cueIcon = QPushButton()
        self.cueIcon.setStyleSheet("""
            QPushButton, QPushButton:pressed {
                padding: 0;
                border: none;
                background-color: transparent;
            }""")
        self.cueIcon.setFocusPolicy(Qt.NoFocus)
        self.cueNameGroup.layout().addWidget(self.cueIcon)
        self.cueIconButton = QPushButton(
            translate("CueAppearanceSettings", "Change icon")
        )
        self.cueIconButton.clicked.connect(self.showIconSelector)
        self.cueNameGroup.layout().addWidget(self.cueIconButton)

        # Description
        self.cueDescriptionGroup = QGroupBox(self)
        self.cueDescriptionGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.cueDescriptionGroup)

        self.cueDescriptionEdit = QTextEdit(self.cueDescriptionGroup)
        self.cueDescriptionEdit.setAcceptRichText(False)
        self.cueDescriptionEdit.setFont(
            QFontDatabase.systemFont(QFontDatabase.FixedFont)
        )
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

        self.colorBButton = ColorButton(self.colorGroup)
        self.colorFButton = ColorButton(self.colorGroup)

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
            translate("CueAppearanceSettings", "Cue Name and Icon")
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
        self.setGroupEnabled(self.cueNameGroup, enabled)
        self.setGroupEnabled(self.cueDescriptionGroup, enabled)
        self.setGroupEnabled(self.fontSizeGroup, enabled)
        self.setGroupEnabled(self.colorGroup, enabled)

    def selectIcon(self, name):
        self.iconName = name
        self.cueIcon.setIcon(IconTheme.get(name))
        self.cueIcon.setIconSize(QSize(34, 34))

    def showIconSelector(self):
        for button in self.iconSelectorDialog.iconButtons:
            QCoreApplication.sendEvent(button, QEvent(QEvent.Leave))
        self.iconSelectorDialog.exec_()

    def getSettings(self):
        settings = {}
        style = {}

        if self.isGroupEnabled(self.cueNameGroup):
            settings["name"] = self.cueNameEdit.text()
            settings["icon"] = self.iconName
        if self.isGroupEnabled(self.cueDescriptionGroup):
            settings["description"] = self.cueDescriptionEdit.toPlainText()
        if self.isGroupEnabled(self.colorGroup):
            if self.colorBButton.color() is not None:
                style["background"] = self.colorBButton.color()
            if self.colorFButton.color() is not None:
                style["color"] = self.colorFButton.color()
        if self.isGroupEnabled(self.fontSizeGroup):
            style["font-size"] = str(self.fontSizeSpin.value()) + "pt"

        if style:
            settings["stylesheet"] = dict_to_css(style)

        return settings

    def loadSettings(self, settings):
        if "name" in settings:
            self.cueNameEdit.setText(settings["name"])
        if "icon" in settings:
            self.iconName = settings["icon"]
            self.cueIcon.setIcon(IconTheme.get(self.iconName))
            self.cueIcon.setIconSize(QSize(34, 34))
        if "description" in settings:
            self.cueDescriptionEdit.setPlainText(settings["description"])
        if "stylesheet" in settings:
            settings = css_to_dict(settings["stylesheet"])
            if "background" in settings:
                self.colorBButton.setColor(settings["background"])
            if "color" in settings:
                self.colorFButton.setColor(settings["color"])
            if "font-size" in settings:
                # [:-2] for removing "pt"
                self.fontSizeSpin.setValue(int(settings["font-size"][:-2]))


class IconSelectorDialog(QDialog):
    def __init__(self, parent=None, onIconSelected=None):
        super().__init__(parent)
        self.setWindowTitle(
            translate("CueAppearanceSettings", "Select an Icon")
        )
        self.onIconSelected = onIconSelected
        self.iconButtons = []
        
        COLUMNS = 5
        layout = QVBoxLayout(self)
        grid = QGridLayout()
        layout.addLayout(grid)

        icon_names = set()
        path = os.path.join(ICON_THEMES_DIR, "lisp/cues")
        for item in os.scandir(path):
            if item.is_file():
                name, _ = os.path.splitext(item.name)
                icon_names.add(name)

        for index, name in enumerate(sorted(icon_names)):
            btn = QToolButton()
            btn.iconName = name
            btn.setIcon(IconTheme.get(name))
            btn.setIconSize(QSize(48, 48))
            btn.setStyleSheet("""
                QToolButton {
                    border: 0px;
                    padding: 10px;
                    margin: 0px;
                    background: transparent;
                }
                QToolButton:hover, QToolButton:focus {
                    background: #4499EE;
                }""")
            btn.clicked.connect(lambda _, n=name: self.clickIcon(n))
            grid.addWidget(btn, index // COLUMNS, index % COLUMNS)
            self.iconButtons.append(btn)

        buttons = QDialogButtonBox(QDialogButtonBox.Cancel)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        buttons.button(QDialogButtonBox.Cancel).setFocus()

    def clickIcon(self, name):
        if self.onIconSelected:
            self.onIconSelected(name)
        self.accept()
        
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if QApplication.focusWidget().iconName:
                self.clickIcon(QApplication.focusWidget().iconName)
