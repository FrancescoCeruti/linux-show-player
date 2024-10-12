# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt6.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QCheckBox,
    QComboBox,
    QGridLayout,
    QLabel,
    QHBoxLayout,
)

from lisp.layout import get_layouts
from lisp.ui.icons import icon_themes_names
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.themes import themes_names
from lisp.ui.ui_utils import translate
from lisp.ui.widgets import LocaleComboBox


class AppGeneral(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "General")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        # Startup "layout"
        self.layoutGroup = QGroupBox(self)
        self.layoutGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.layoutGroup)

        self.startupDialogCheck = QCheckBox(self.layoutGroup)
        self.layoutGroup.layout().addWidget(self.startupDialogCheck, 0, 0, 1, 2)

        self.layoutLabel = QLabel(self.layoutGroup)
        self.layoutGroup.layout().addWidget(self.layoutLabel, 1, 0)

        self.layoutCombo = QComboBox(self.layoutGroup)
        self.layoutGroup.layout().addWidget(self.layoutCombo, 1, 1)
        # Get available layouts
        for layout in get_layouts():
            self.layoutCombo.addItem(layout.NAME, layout.__name__)

        # Enable/Disable layout selection
        self.startupDialogCheck.stateChanged.connect(
            self.layoutCombo.setDisabled
        )
        self.startupDialogCheck.stateChanged.connect(
            self.layoutLabel.setDisabled
        )

        # Application theme
        self.themeGroup = QGroupBox(self)
        self.themeGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.themeGroup)

        self.themeLabel = QLabel(self.themeGroup)
        self.themeGroup.layout().addWidget(self.themeLabel, 0, 0)
        self.themeCombo = QComboBox(self.themeGroup)
        self.themeCombo.addItems(themes_names())
        self.themeGroup.layout().addWidget(self.themeCombo, 0, 1)

        self.iconsLabel = QLabel(self.themeGroup)
        self.themeGroup.layout().addWidget(self.iconsLabel, 1, 0)
        self.iconsCombo = QComboBox(self.themeGroup)
        self.iconsCombo.addItems(sorted(icon_themes_names()))
        self.themeGroup.layout().addWidget(self.iconsCombo, 1, 1)

        self.themeGroup.layout().setColumnStretch(0, 1)
        self.themeGroup.layout().setColumnStretch(1, 1)

        # Locale
        self.localeGroup = QGroupBox(self)
        self.localeGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.localeGroup)

        self.localeLabel = QLabel(self.localeGroup)
        self.localeGroup.layout().addWidget(self.localeLabel)
        self.localeCombo = LocaleComboBox(self.localeGroup)
        self.localeGroup.layout().addWidget(self.localeCombo)

        self.retranslateUi()

    def retranslateUi(self):
        self.layoutGroup.setTitle(
            translate("AppGeneralSettings", "Default layout")
        )
        self.startupDialogCheck.setText(
            translate("AppGeneralSettings", "Show layout selection at startup")
        )
        self.layoutLabel.setText(
            translate("AppGeneralSettings", "Use layout at startup:")
        )
        self.themeGroup.setTitle(
            translate("AppGeneralSettings", "Application themes")
        )
        self.themeLabel.setText(translate("AppGeneralSettings", "UI theme:"))
        self.iconsLabel.setText(translate("AppGeneralSettings", "Icons theme:"))

        self.localeGroup.setTitle(
            translate(
                "AppGeneralSettings", "Application language (require a restart)"
            )
        )
        self.localeLabel.setText(translate("AppGeneralSettings", "Language:"))

    def getSettings(self):
        settings = {
            "theme": {
                "theme": self.themeCombo.currentText(),
                "icons": self.iconsCombo.currentText(),
            },
            "locale": self.localeCombo.currentLocale(),
            "layout": {},
        }

        if self.startupDialogCheck.isChecked():
            settings["layout"]["default"] = "NoDefault"
        else:
            settings["layout"]["default"] = self.layoutCombo.currentData()

        return settings

    def loadSettings(self, settings):
        layout_name = settings["layout"]["default"]
        if layout_name.lower() == "nodefault":
            self.startupDialogCheck.setChecked(True)
        else:
            self.layoutCombo.setCurrentIndex(
                self.layoutCombo.findData(layout_name)
            )

        self.themeCombo.setCurrentText(settings["theme"]["theme"])
        self.iconsCombo.setCurrentText(settings["theme"]["icons"])
        self.localeCombo.setCurrentLocale(settings["locale"])
