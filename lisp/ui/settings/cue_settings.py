# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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

from copy import deepcopy
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QTabWidget, QDialogButtonBox

from lisp.ui.settings.sections.cue_general import CueGeneralSettings
from lisp.utils.util import deep_update


class CueSettings(QDialog):
    on_apply = QtCore.pyqtSignal(dict)

    def __init__(self, widgets=(), cue=None, check=False, **kwargs):
        super().__init__(**kwargs)

        conf = {}

        if cue is not None:
            conf = deepcopy(cue.properties())
            self.setWindowTitle(conf['name'])

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setMaximumSize(635, 530)
        self.setMinimumSize(635, 530)
        self.resize(635, 530)

        self.sections = QTabWidget(self)
        self.sections.setGeometry(QtCore.QRect(5, 10, 625, 470))

        wsize = QtCore.QSize(625, 470 - self.sections.tabBar().height())

        for widget in widgets:
            widget = widget(wsize, cue)
            widget.set_configuration(conf)
            widget.enable_check(check)
            self.sections.addTab(widget, widget.Name)

        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setGeometry(10, 490, 615, 30)
        self.dialogButtons.setStandardButtons(QDialogButtonBox.Cancel |
                                              QDialogButtonBox.Ok |
                                              QDialogButtonBox.Apply)

        self.dialogButtons.rejected.connect(self.reject)
        self.dialogButtons.accepted.connect(self.accept)
        apply = self.dialogButtons.button(QDialogButtonBox.Apply)
        apply.clicked.connect(self.apply)

    def accept(self):
        self.apply()
        super().accept()

    def apply(self):
        new_conf = {}

        for n in range(self.sections.count()):
            deep_update(new_conf, self.sections.widget(n).get_configuration())

        self.on_apply.emit(new_conf)
