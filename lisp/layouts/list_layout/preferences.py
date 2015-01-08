##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtWidgets import *  # @UnusedWildImport

from lisp.ui.settings.section import SettingsSection


class ListLayoutPreferences(SettingsSection):

    NAME = 'List Layout'

    def __init__(self, size, parent=None):
        super().__init__(size, parent)

        self.behaviorsGroup = QGroupBox(self)
        self.behaviorsGroup.setTitle('Default behaviors')
        self.behaviorsGroup.setLayout(QVBoxLayout())
        self.behaviorsGroup.setGeometry(0, 0, self.width(), 120)

        self.showDbMeters = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showDbMeters)

        self.showAccurate = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showAccurate)

        self.showSeek = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showSeek)

        self.autoNext = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.autoNext)

        self.retranslateUi()

    def retranslateUi(self):
        self.behaviorsGroup.setTitle('Default behaviors')
        self.showDbMeters.setText('Show db-meters')
        self.showAccurate.setText('Show accurate time')
        self.showSeek.setText('Show seek sliders')
        self.autoNext.setText('Automatically select the next cue')

    def get_configuration(self):
        conf = {}

        conf['showdbmeters'] = str(self.showDbMeters.isChecked())
        conf['showseek'] = str(self.showSeek.isChecked())
        conf['showaccurate'] = str(self.showAccurate.isChecked())
        conf['autonext'] = str(self.autoNext.isChecked())

        return {'ListLayout': conf}

    def set_configuration(self, conf):
        settings = conf.get('ListLayout', {})

        self.showDbMeters.setChecked(settings.get('showdbmeters') == 'True')
        self.showAccurate.setChecked(settings.get('showaccurate') == 'True')
        self.showSeek.setChecked(settings.get('showseek') == 'True')
        self.autoNext.setChecked(settings.get('autonext') == 'True')
