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

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from lisp.core.class_based_registry import ClassBasedRegistry
from lisp.core.singleton import Singleton
from lisp.core.util import typename
from lisp.cues.cue import Cue
from lisp.ui.settings.pages import CuePageMixin, SettingsPagesTabWidget
from lisp.ui.ui_utils import translate


class CueSettingsRegistry(ClassBasedRegistry, metaclass=Singleton):
    def add(self, item, ref_class=Cue):
        return super().add(item, ref_class)

    def filter(self, ref_class=Cue):
        return super().filter(ref_class)

    def clear_class(self, ref_class=Cue):
        return super().filter(ref_class)


class CueSettingsDialog(QDialog):
    onApply = QtCore.pyqtSignal(dict)

    def __init__(self, cue, **kwargs):
        """

        :param cue: Target cue, or a cue-type for multi-editing
        """
        super().__init__(**kwargs)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setMaximumSize(640, 510)
        self.setMinimumSize(640, 510)
        self.resize(640, 510)
        self.setLayout(QVBoxLayout())
        # self.layout().setContentsMargins(5, 5, 5, 10)

        if isinstance(cue, type):
            if issubclass(cue, Cue):
                cue_properties = cue.class_defaults()
                cue_class = cue
            else:
                raise TypeError(
                    "invalid cue type, must be a Cue subclass or a Cue object, "
                    "not {}".format(cue.__name__)
                )
        elif isinstance(cue, Cue):
            self.setWindowTitle(cue.name)
            cue_properties = cue.properties()
            cue_class = cue.__class__
        else:
            raise TypeError(
                "invalid cue type, must be a Cue subclass or a Cue object, "
                "not {}".format(typename(cue))
            )

        self.mainPage = SettingsPagesTabWidget(parent=self)
        self.mainPage.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.mainPage)

        def sk(widget):
            # Sort-Key function
            return translate("SettingsPageName", widget.Name)

        for page in sorted(CueSettingsRegistry().filter(cue_class), key=sk):
            if issubclass(page, CuePageMixin):
                settings_widget = page(cue_class)
            else:
                settings_widget = page()

            settings_widget.loadSettings(cue_properties)
            settings_widget.enableCheck(cue is cue_class)
            self.mainPage.addPage(settings_widget)

        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setStandardButtons(
            QDialogButtonBox.Cancel
            | QDialogButtonBox.Apply
            | QDialogButtonBox.Ok
        )
        self.layout().addWidget(self.dialogButtons)

        self.dialogButtons.button(QDialogButtonBox.Cancel).clicked.connect(
            self.reject
        )
        self.dialogButtons.button(QDialogButtonBox.Apply).clicked.connect(
            self.__onApply
        )
        self.dialogButtons.button(QDialogButtonBox.Ok).clicked.connect(
            self.__onOk
        )

    def loadSettings(self, settings):
        self.mainPage.loadSettings(settings)

    def getSettings(self):
        return self.mainPage.getSettings()

    def __onApply(self):
        self.onApply.emit(self.getSettings())

    def __onOk(self):
        self.__onApply()
        self.accept()
