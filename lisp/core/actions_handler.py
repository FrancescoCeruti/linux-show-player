##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################


from collections import deque
import logging

from PyQt5.QtCore import pyqtSignal, QObject
from lisp.utils import configuration as cfg

from lisp.core.action import Action
from lisp.core.singleton import QSingleton


class ActionsHandler(QObject, metaclass=QSingleton):

    MaxStackSize = int(cfg.config['Actions']['MaxStackSize'])

    action_done = pyqtSignal(Action)
    action_undone = pyqtSignal(Action)
    action_redone = pyqtSignal(Action)

    def __init__(self):
        super().__init__()

        self._undo = deque()
        self._redo = deque()
        if self.MaxStackSize > 0:
            self._undo.maxlen = self.MaxStackSize
            self._redo.maxlen = self.MaxStackSize

        self._saved = False
        self._saved_action = None

    def clear(self):
        self._undo.clear()
        self._redo.clear()
        self._saved_action = None

    def do_action(self, action):
        action.do()

        self._logging(action, 'Last action: ')
        self._undo.append(action)
        # Clean the redo stack for maintain consistency
        self._redo.clear()
        self._saved = False

        self.action_done.emit(action)

    def undo_action(self):
        if len(self._undo) > 0:
            action = self._undo.pop()
            action.undo()

            self._logging(action, 'Undo: ')
            self._redo.append(action)
            self._saved = False

            self.action_undone.emit(action)

    def redo_action(self):
        if len(self._redo) > 0:
            action = self._redo.pop()
            action.redo()

            self._logging(action, 'Redo: ')
            self._undo.append(action)
            self._saved = False

            self.action_redone.emit(action)

    def set_saved(self):
        self._saved = True
        if len(self._undo) > 0:
            self._saved_action = self._undo[-1]

    def is_saved(self):
        if len(self._undo) > 0:
            return self._saved or self._undo[-1] is self._saved_action
        else:
            return True

    def _logging(self, action, pre,):
        message = action.log()
        if message.strip() == '':
            message = action.__class__.__name__

        logging.info(pre + message)
