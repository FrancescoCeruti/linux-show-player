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

import os

from PyQt5.QtCore import (
    Qt,
    QSize,
    QT_TRANSLATE_NOOP,
)
from PyQt5.QtGui import QFontDatabase, QStandardItemModel, QStandardItem
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
    QDialogButtonBox,
    QListWidget,
    QListView,
    QStyledItemDelegate,
    QStyleOptionViewItem,
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

        self.iconSelectorDialog = None

        # Name and Icon
        self.cueNameGroup = QGroupBox(self)
        self.cueNameGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.cueNameGroup)

        self.cueIconPreview = QLabel(self)
        self.cueNameGroup.layout().addWidget(self.cueIconPreview)

        self.cueIconButton = QPushButton(self)
        self.cueIconButton.clicked.connect(self.showIconSelector)
        self.cueNameGroup.layout().addWidget(self.cueIconButton)

        self.cueNameEdit = QLineEdit(self.cueNameGroup)
        self.cueNameGroup.layout().addWidget(self.cueNameEdit)

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
        self.cueIconButton.setText(
            translate("CueAppearanceSettings", "Change icon")
        )
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

    def showIconSelector(self):
        if self.iconSelectorDialog is None:
            self.iconSelectorDialog = IconSelectorDialog(self)

        self.iconSelectorDialog.setSelectedIcon(self.iconName)

        if self.iconSelectorDialog.exec() == QDialog.Accepted:
            self.iconName = self.iconSelectorDialog.getSelectedIcon("led")
            self.updateIconPreview()

    def updateIconPreview(self):
        self.cueIconPreview.setPixmap(
            IconTheme.get(self.iconName).pixmap(20, 20)
        )

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
            self.updateIconPreview()
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowModality(Qt.ApplicationModal)
        self.setLayout(QVBoxLayout())

        self.iconsModel = QStandardItemModel()
        self.iconsList = QListView(self)
        self.iconsList.setModel(self.iconsModel)
        self.iconsList.setItemDelegate(IconOnlyDelegate())
        self.iconsList.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.iconsList.setFixedWidth(350)
        self.iconsList.setMinimumHeight(350)
        self.iconsList.setViewMode(QListWidget.IconMode)
        self.iconsList.setResizeMode(QListWidget.Adjust)
        self.iconsList.setFlow(QListWidget.LeftToRight)
        self.iconsList.setUniformItemSizes(True)
        self.iconsList.setWrapping(True)
        self.iconsList.setIconSize(QSize(48, 48))
        self.iconsList.setSpacing(10)
        self.iconsList.activated.connect(self.accept)
        self.iconsList.clicked.connect(self.accept)
        self.layout().addWidget(self.iconsList)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Cancel, self)
        self.buttons.rejected.connect(self.reject)
        self.layout().addWidget(self.buttons)

        for name in self.fetchIcons():
            item = QStandardItem()
            item.setData(name, Qt.UserRole)
            item.setIcon(IconTheme.get(name))

            self.iconsModel.appendRow(item)

        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(
            translate("CueAppearanceSettings", "Select an Icon")
        )

    def fetchIcons(self):
        icons = set()

        for item in os.scandir(os.path.join(ICON_THEMES_DIR, "lisp/cues")):
            if item.is_file():
                name, _ = os.path.splitext(item.name)
                icons.add(name)

        return sorted(icons)

    def getSelectedIcon(self, fallback=None):
        if self.iconsList.currentIndex().isValid():
            return self.iconsModel.data(
                self.iconsList.currentIndex(), Qt.UserRole
            )

        return fallback

    def setSelectedIcon(self, name):
        for row in range(self.iconsModel.rowCount()):
            item = self.iconsModel.item(row)
            if item.data(Qt.UserRole) == name:
                self.iconsList.setCurrentIndex(item.index())


class IconOnlyDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)

        option.features &= ~QStyleOptionViewItem.HasDisplay
