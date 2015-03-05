##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################
from PyQt5.QtWidgets import QTimeEdit


class TimeEdit(QTimeEdit):

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self._sections_steps = {}
        self._msec_rounded = False

    def setSectionStep(self, section, step):
        if not isinstance(section, QTimeEdit.Section):
            raise AttributeError('Not a QTimeEdit.Section')
        if step <= 0:
            raise AttributeError('Step value must be >= 0')

        self._sections_steps[section] = step

    def stepBy(self, value):
        if abs(value) != self._sections_steps.get(self.currentSection(), 1):
            sign = 1 if value >= 0 else -1
            value = sign * self._sections_steps.get(self.currentSection(), 1)

        super().stepBy(value)