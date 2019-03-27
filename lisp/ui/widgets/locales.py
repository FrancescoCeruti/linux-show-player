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

from enum import Enum

from PyQt5.QtCore import QT_TRANSLATE_NOOP, Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QStyledItemDelegate,
    QWidget,
    QGridLayout,
    QDoubleSpinBox,
    QLabel,
)

from lisp.ui.icons import IconTheme
from PyQt5.QtCore import QLocale
from lisp.ui.ui_utils import translate

try:
    from os import scandir
except ImportError:
    from scandir import scandir


class LocaleEdit(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.locales = self.localesFromFile()

        self.setLayout(QGridLayout())
        self.localeLabel = QLabel(self)
        self.layout().addWidget(self.localeLabel, 0, 0)
        self.localeCombo = QComboBox(self)
        self.localeCombo.addItems(self.getLanguagesUi())
        self.layout().addWidget(self.localeCombo, 0, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.localeLabel.setText(translate("AppGeneralSettings", "Languages:"))

    def setLocale(self, locale):
        self.localeCombo.setCurrentText(locale)

    def getCurrentText(self):
        return self.getLocaleFromLanguageUi(self.localeCombo.currentText())

    def getLocaleFromLanguageUi(self, languageUi):
        for loc, lang in self.locales.items():
            if lang == languageUi:
                 return loc

    def getLocaleLabel(self):
        return self.localeLabel

    def getLocaleCombo(self):
        return self.localeCombo

    def getLocales(self):
        return self.locales

    def localesFromFile(self):
        loc = {}
        for entry in scandir("lisp/i18n/ts/"):
            if entry.is_dir():
                ql = QLocale(entry.name)
                loc[entry.name[:2]] = "{} ({})".format(
                    QLocale.languageToString(
                        ql.language()),ql.nativeLanguageName()
                    )
        return loc

    def getLanguagesUi(self):
        languagesUi = []
        for l in self.locales:
            languagesUi.append(self.locales[l]);
        return languagesUi;

