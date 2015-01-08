##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5 import QtCore
from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import *  # @UnusedWildImport
from lisp.ui.mainwindow import MainWindow

from lisp.application import Application
from lisp.cues.action_cue import ActionCue
from lisp.cues.cue_factory import CueFactory
from lisp.cues.media_cue import MediaCue
from lisp.layouts.cue_layout import CueLayout
from lisp.modules.action_cues.action_cues_factory import ActionCueFactory
from lisp.ui.cuelistdialog import CueListDialog
from lisp.ui.settings.section import SettingsSection


class SeekAction(ActionCue):

    Name = 'Seek action'

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.update_properties({'target_id': -1, 'time': -1})

    def execute(self, emit=True):
        super().execute(emit)

        # Get the cue every time because the reference may change
        layout = Application().layout
        cue = layout.get_cue_by_id(self['target_id'])

        if isinstance(cue, MediaCue) and self['time'] >= 0:
            cue.media.seek(self['time'])

    def update_properties(self, properties):
        super().update_properties(properties)


class SeekSettings(SettingsSection):

    Name = 'Seek Settings'

    def __init__(self, size, cue=None, parent=None):
        super().__init__(size, cue=cue, parent=parent)

        self.cue_id = -1
        self.setLayout(QVBoxLayout(self))

        self.app_layout = Application().layout
        self.cueDialog = CueListDialog(parent=self)
        self.cueDialog.add_cues(self.app_layout.get_cues(cue_class=MediaCue))

        self.cueGroup = QGroupBox(self)
        self.cueGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.cueGroup)

        self.cueButton = QPushButton(self.cueGroup)
        self.cueButton.clicked.connect(self.select_cue)
        self.cueGroup.layout().addWidget(self.cueButton)

        self.cueLabel = QLabel(self.cueGroup)
        self.cueLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.cueGroup.layout().addWidget(self.cueLabel)

        self.seekGroup = QGroupBox(self)
        self.seekGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.seekGroup)

        self.seekEdit = QTimeEdit(self.seekGroup)
        self.seekEdit.setDisplayFormat('HH.mm.ss.zzz')
        self.seekGroup.layout().addWidget(self.seekEdit)

        self.seekLabel = QLabel(self.seekGroup)
        self.seekLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.seekGroup.layout().addWidget(self.seekLabel)

        self.layout().addSpacing(200)

        self.retranslateUi()

    def retranslateUi(self):
        self.cueGroup.setTitle('Cue')
        self.cueButton.setText('Click to select')
        self.cueLabel.setText('Not selected')
        self.seekGroup.setTitle('Seek')
        self.seekLabel.setText('Time to reach')

    def select_cue(self):
        if self.cueDialog.exec_() == self.cueDialog.Accepted:
            cue = self.cueDialog.selected_cues()[0]

            self.cue_id = cue['id']
            self.seekEdit.setMaximumTime(
                QTime.fromMSecsSinceStartOfDay(cue.media['duration']))
            self.cueLabel.setText(cue['name'])

    def enable_check(self, enable):
        self.cueGroup.setCheckable(enable)
        self.cueGroup.setChecked(False)

        self.seekGroup.setCheckable(enable)
        self.seekGroup.setChecked(False)

    def get_configuration(self):
        return {'target_id': self.cue_id,
                'time': self.seekEdit.time().msecsSinceStartOfDay()}

    def set_configuration(self, conf):
        if conf is not None:
            cue = self.app_layout.get_cue_by_id(conf['target_id'])
            if cue is not None:
                self.cue_id = conf['target_id']
                self.seekEdit.setTime(
                    QTime.fromMSecsSinceStartOfDay(conf['time']))
                self.seekEdit.setMaximumTime(
                    QTime.fromMSecsSinceStartOfDay(cue.media['duration']))
                self.cueLabel.setText(cue['name'])


CueFactory.register_factory('SeekAction', ActionCueFactory)
MainWindow().register_cue_options_ui(SeekAction.Name,
                                     lambda: [{'name': SeekAction.Name,
                                               'type': 'SeekAction'}],
                                     category='Action cues')
CueLayout.add_settings_section(SeekSettings, SeekAction)
