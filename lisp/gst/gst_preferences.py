##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtWidgets import QVBoxLayout, QPushButton

from lisp.gst.gst_pipe_edit import GstPipeEdit
from lisp.ui.settings.section import SettingsSection


class GstPreferences(SettingsSection):

    NAME = 'GStreamer settings'

    def __init__(self, size, parent=None):
        super().__init__(size, parent)

        self.setLayout(QVBoxLayout())

        self.editPipeline = QPushButton(self)
        self.editPipeline.setText('Change default pipeline')
        self.editPipeline.clicked.connect(self.show_dialog)
        self.layout().addWidget(self.editPipeline)
        self.layout().addSpacing(self.height() - 80)

    def show_dialog(self):
        edit = GstPipeEdit(self._pipe, preferences_mode=True)
        if edit.exec_() == edit.Accepted:
            self._pipe = edit.get_pipe()

    def get_configuration(self):
        return {'Gst': {'pipeline': self._pipe}}

    def set_configuration(self, conf):
        self._pipe = conf['Gst']['pipeline'].replace(' ', '')
