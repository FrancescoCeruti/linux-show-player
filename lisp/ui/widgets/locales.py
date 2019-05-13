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

from PyQt5.QtCore import QLocale
from PyQt5.QtWidgets import QComboBox

from lisp.ui.ui_utils import search_translations


class LocaleComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._locales = [""]
        self._locales.extend(search_translations())
        for locale in self._locales:
            self.addItem(self._localeUiText(locale), locale)

    def setCurrentLocale(self, locale):
        try:
            self.setCurrentIndex(self._locales.index(locale))
        except IndexError:
            pass

    def currentLocale(self):
        return self.currentData()

    @staticmethod
    def _localeUiText(locale):
        if locale:
            ql = QLocale(locale)
            return "{} ({})".format(
                ql.languageToString(ql.language()), ql.nativeLanguageName()
            )
        else:
            return "System ({})".format(QLocale().system().nativeLanguageName())
