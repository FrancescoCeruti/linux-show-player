##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################


from PyQt5 import QtCore
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QHBoxLayout, QLineEdit, \
    QSizePolicy, QLabel, QComboBox
from lisp.ui.mainwindow import MainWindow

from lisp.application import Application
from lisp.cues.action_cue import ActionCue
from lisp.cues.cue_factory import CueFactory
from lisp.cues.media_cue import MediaCue
from lisp.layouts.cue_layout import CueLayout
from lisp.modules.action_cues.action_cues_factory import ActionCueFactory
from lisp.ui.settings.section import SettingsSection
from lisp.utils.decorators import async


class GroupsAction(ActionCue):

    ACTION_PLAY = 'Play'
    ACTION_PAUSE = 'Pause'
    ACTION_STOP = 'Stop'
    ACTION_AUTO = 'Auto'

    Name = 'Groups action'

    def __init__(self, **kwds):
        super().__init__(**kwds)

        self.update_properties({'groups': [], 'action': None})

    @async
    def execute(self, emit=True):
        super().execute(emit)

        layout = Application().layout
        for cue in layout.get_cues(cue_class=MediaCue):
            if not set(cue['groups']).isdisjoint(self['groups']):
                if self['action'] == self.ACTION_PLAY:
                    cue.media.play()
                elif self['action'] == self.ACTION_PAUSE:
                    cue.media.pause()
                elif self['action'] == self.ACTION_STOP:
                    cue.media.stop()
                elif self['action'] == self.ACTION_AUTO:
                    cue.execute()


class GroupsActionSettings(SettingsSection):

    Name = 'Cue Settings'

    ACTIONS = ['Play', 'Pause', 'Stop', 'Auto']

    def __init__(self, size, cue=None, parent=None):
        super().__init__(size, cue=cue, parent=parent)

        self.setLayout(QVBoxLayout(self))

        # Groups
        self.groupGroups = QGroupBox(self)
        self.groupGroups.setTitle("Edit groups")
        self.ggHLayout = QHBoxLayout(self.groupGroups)

        self.editGroups = QLineEdit(self.groupGroups)
        regex = QtCore.QRegExp('(\d+,)*')
        self.editGroups.setValidator(QRegExpValidator(regex))
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.editGroups.setSizePolicy(sizePolicy)
        self.ggHLayout.addWidget(self.editGroups)

        self.groupsEditLabel = QLabel(self.groupGroups)
        self.groupsEditLabel.setText("Modify groups [0,1,2,...,n]")
        self.groupsEditLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.ggHLayout.addWidget(self.groupsEditLabel)

        self.layout().addWidget(self.groupGroups)

        # Action
        self.groupAction = QGroupBox(self)
        self.groupAction.setTitle("Select action")
        self.gaHLayout = QHBoxLayout(self.groupAction)

        self.actionsBox = QComboBox(self.groupAction)
        self.actionsBox.addItems(self.ACTIONS)
        self.gaHLayout.addWidget(self.actionsBox)

        self.layout().addWidget(self.groupAction)
        self.layout().addSpacing(self.height() - 200)

    def get_configuration(self):
        conf = {}

        checkable = self.groupGroups.isCheckable()

        if not (checkable and not self.groupGroups.isChecked()):
            groups_str = self.editGroups.text().split(',')
            if groups_str[-1] != '':
                conf['groups'] = [int(groups_str[-1])]
            else:
                conf['groups'] = []
            conf['groups'] += [int(g) for g in groups_str[:-1]]
        if not (checkable and not self.groupAction.isChecked()):
            conf['action'] = self.actionsBox.currentText()

        return conf

    def enable_check(self, enable):
        self.groupGroups.setCheckable(enable)
        self.groupGroups.setChecked(False)

        self.groupAction.setCheckable(enable)
        self.groupAction.setChecked(False)

    def set_configuration(self, conf):
        if 'groups' in conf:
            self.editGroups.setText(str(conf['groups'])[1:-1])
        if 'action' in conf and conf['action'] in self.ACTIONS:
            self.actionsBox.setCurrentIndex(self.ACTIONS.index(conf['action']))


CueFactory.register_factory('GroupsAction', ActionCueFactory)
MainWindow().register_cue_options_ui(GroupsAction.Name,
                                     lambda: [{'name': GroupsAction.Name,
                                               'type': 'GroupsAction'}],
                                     category='Action cues')
CueLayout.add_settings_section(GroupsActionSettings, GroupsAction)
