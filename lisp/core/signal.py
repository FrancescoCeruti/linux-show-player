##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from types import FunctionType, MethodType


class Signal:
    '''Simple signal'''

    def __init__(self):
        self._slots = []

    def connect(self, slot):
        if isinstance(slot, FunctionType) or isinstance(slot, MethodType):
            self._slots.append(slot)

    def disconnect(self, slot):
        if isinstance(slot, FunctionType) or isinstance(slot, MethodType):
            try:
                self._slots.remove(slot)
            except(ValueError):
                pass

    def emit(self, *argv, **kargv):
        for act in self._slots:
            act(*argv, **kargv)
