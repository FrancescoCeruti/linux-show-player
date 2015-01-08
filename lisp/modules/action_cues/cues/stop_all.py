##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtWidgets import *  # @UnusedWildImport
from lisp.ui.mainwindow import MainWindow

from lisp.application import Application
from lisp.cues.action_cue import ActionCue
from lisp.cues.cue_factory import CueFactory
from lisp.cues.media_cue import MediaCue
from lisp.layouts.cue_layout import CueLayout
from lisp.modules.action_cues.action_cues_factory import ActionCueFactory
from lisp.ui.settings.section import SettingsSection
from lisp.utils.decorators import async


class StopAll(ActionCue):

    Name = 'Stop-all'

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.update_properties({'pause_mode': False})

    @async
    def execute(self, emit=True):
        super().execute(emit)

        layout = Application().layout
        for cue in layout.get_cues(cue_class=MediaCue):
            if self['pause_mode']:
                cue.media.pause()
            else:
                cue.media.stop()


class StopAllSettings(SettingsSection):

    Name = 'Cue Settings'

    def __init__(self, size, cue=None, parent=None):
        super().__init__(size, cue=cue, parent=parent)

        self.setLayout(QVBoxLayout(self))

        self.group = QGroupBox(self)
        self.group.setTitle('Mode')
        self.group.setLayout(QHBoxLayout(self.group))

        self.pauseMode = QCheckBox(self.group)
        self.pauseMode.setText('Pause mode')
        self.group.layout().addWidget(self.pauseMode)

        self.layout().addWidget(self.group)
        self.layout().addSpacing(self.height() - 100)

    def enable_check(self, enable):
        self.group.setCheckable(enable)
        self.group.setChecked(False)

    def get_configuration(self):
        conf = {}

        if not (self.group.isCheckable() and not self.group.isChecked()):
            conf['pause_mode'] = self.pauseMode.isChecked()

        return conf

    def set_configuration(self, conf):
        if 'pause_mode' in conf:
            self.pauseMode.setChecked(conf['pause_mode'])

CueFactory.register_factory('StopAll', ActionCueFactory)
MainWindow().register_cue_options_ui(StopAll.Name,
                                     lambda:  [{'name': StopAll.Name,
                                                'type': 'StopAll'}],
                                     category='Action cues')
CueLayout.add_settings_section(StopAllSettings, StopAll)
