##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QListWidget, QStackedWidget, \
    QDialogButtonBox

from lisp.utils.util import deep_update


class AppSettings(QDialog):

    SettingsWidgets = []

    def __init__(self, conf, **kwargs):
        super().__init__(**kwargs)

        self.conf = conf
        self.setWindowTitle('LiSP preferences')

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setMaximumSize(635, 530)
        self.setMinimumSize(635, 530)
        self.resize(635, 530)

        self.listWidget = QListWidget(self)
        self.listWidget.setGeometry(QtCore.QRect(5, 10, 185, 470))

        self.sections = QStackedWidget(self)
        self.sections.setGeometry(QtCore.QRect(200, 10, 430, 470))

        for widget in self.SettingsWidgets:
            widget = widget(QtCore.QSize(430, 465), self)
            widget.set_configuration(self.conf)

            self.listWidget.addItem(widget.NAME)
            self.sections.addWidget(widget)

        if len(self.SettingsWidgets) > 0:
            self.listWidget.setCurrentRow(0)

        self.listWidget.currentItemChanged.connect(self._change_page)

        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setGeometry(10, 495, 615, 30)
        self.dialogButtons.setStandardButtons(QDialogButtonBox.Cancel |
                                              QDialogButtonBox.Ok)

        self.dialogButtons.rejected.connect(self.reject)
        self.dialogButtons.accepted.connect(self.accept)

    def get_configuraton(self):
        conf = {}

        for n in range(self.sections.count()):
            widget = self.sections.widget(n)
            newconf = widget.get_configuration()
            deep_update(conf, newconf)

        return conf

    @classmethod
    def register_settings_widget(cls, widget):
        if widget not in cls.SettingsWidgets:
            cls.SettingsWidgets.append(widget)

    @classmethod
    def unregister_settings_widget(cls, widget):
        if widget not in cls.SettingsWidgets:
            cls.SettingsWidgets.remove(widget)

    def _change_page(self, current, previous):
        if not current:
            current = previous

        self.sections.setCurrentIndex(self.listWidget.row(current))
