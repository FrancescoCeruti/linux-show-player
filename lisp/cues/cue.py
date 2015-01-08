##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from uuid import uuid4

from PyQt5.QtCore import QObject, pyqtSignal


class Cue(QObject):

    executed = pyqtSignal(object)
    updated = pyqtSignal(object)

    def __init__(self, cue_id=None, **kwds):
        super().__init__(**kwds)

        self.__finalized = False
        self._properties = {'id': str(uuid4()) if cue_id is None else cue_id,
                            'index': -1,
                            'groups': [],
                            'name': 'Untitled'}

    def cue_id(self):
        return self._properties['id']

    def __do__(self):
        pass

    def execute(self, emit=True):
        if emit:
            self.executed.emit(self)

    def properties(self):
        return self._properties

    def update_properties(self, properties):
        self._properties.update(properties)
        self.updated.emit(self)

    def finalize(self):
        '''Finalize the cue.'''
        self.__finalized = True

    def is_finalized(self):
        return self.__finalized

    def __getitem__(self, key):
        return self.properties()[key]

    def __setitem__(self, key, value):
        self._properties[key] = value
