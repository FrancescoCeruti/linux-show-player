##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################


from collections import deque
from queue import Queue
import logging

from PyQt5.QtCore import QThread, pyqtSignal
from lisp.utils import configuration as cfg

from lisp.actions.action import Action
from lisp.core.singleton import QSingleton


class ActionsHandler(QThread, metaclass=QSingleton):

    StacksSize = int(cfg.config['Actions']['StacksSize'])
    LogEnabled = cfg.config['Actions']['Log'] == 'True'

    logging = pyqtSignal(str)
    action_performed = pyqtSignal(Action)

    # Allow (qt)thread-safe call
    _safe_call_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()

        self._safe_call_signal.connect(lambda f: f())
        self._actionsQueue = Queue()
        self._sessions = {'main': (deque(), deque())}

        self.start()

    def clear_session(self, session='main'):
        self._sessions[session] = (deque(), deque())

    def add_session(self, session):
        if session not in self._sessions:
            self._sessions[session] = (deque(), deque())

    def del_session(self, session):
        if session in self._sessions and session != 'main':
            self._sessions.pop(session)

    def do_action(self, action, session='main'):
        if Action is not None and session in self._sessions:
            self._actionsQueue.put((session, action))

    def undo_action(self, session='main'):
        if session in self._sessions:
            stack = self._sessions[session][0]
            if len(stack) > 0:
                action = stack.pop()
                self._safe_call_signal.emit(action.undo)
                self._log(action, 'Undo: ')

                # Add the action into the redo stack
                stack = self._sessions[session][1]
                self._arrange_stack(stack)
                stack.append(action)

    def redo_action(self, session='main'):
        if session in self._sessions:
            stack = self._sessions[session][1]
            if len(stack) > 0:
                action = stack.pop()
                self._safe_call_signal.emit(action.redo)
                self._log(action, 'Redo: ')

                # Add the action into the undo stack
                stack = self._sessions[session][0]
                self._arrange_stack(stack)
                stack.append(action)

    def run(self):
        while True:
            session, action = self._actionsQueue.get()
            self._safe_call_signal.emit(action.do)
            self._log(action, 'Last action: ')

            if session not in self._sessions:
                self._sessions[session] = (deque(), deque())

            self._arrange_stack(self._sessions[session][0])
            self._sessions[session][0].append(action)

            # Clean the redo stack for maintain consistency
            self._sessions[session][1].clear()

            del action

    def _arrange_stack(self, stack):
        if self.StacksSize > 0 and len(stack) == self.StacksSize:
            stack.popleft()

    def _log(self, action, pre='', post=''):
        if self.LogEnabled:
            if action.log().strip() != '':
                self.logging.emit(pre + action.log() + post)
                logging.info(pre + action.log() + post)
