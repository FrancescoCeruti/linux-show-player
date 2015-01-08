##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtWidgets import QTreeWidgetItem


class ActionItem(QTreeWidgetItem):

    def __init__(self, cue, **kwds):
        super().__init__(**kwds)

        self.selected = False
        self.cue = cue

        self.setText(1, cue['name'])
        self.cue.updated.connect(self.update_item)

    def update_item(self):
        self.setText(1, self.cue['name'])

    def select(self):
        self.selected = not self.selected
