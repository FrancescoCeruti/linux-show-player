##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from abc import abstractmethod

from PyQt5.QtCore import pyqtSignal, QObject

from lisp.core.qmeta import QABCMeta


class Media(QObject,  metaclass=QABCMeta):
    '''
        An unique interface for all the media in the application.

        In various class functions, the parameter "emit" is used for decide
        when a signal should be emitted.
    '''

    '''
        Media status: describe the current media state.
        NOTE: Can be different from current real playback state.
    '''
    PLAYING = 3  # Media in play
    PAUSED = 2   # Media in pause
    STOPPED = 1  # Media ready for playback
    NONE = 0     # Media not configured

    '''
        Notification signals, emitted when the media state will be changed
        or when it is  changed, the first (emitted) parameter will be the
        media reference.
    '''
    paused = pyqtSignal(object)         # After pause
    played = pyqtSignal(object)         # After play
    sought = pyqtSignal(object, int)    # After seek
    stopped = pyqtSignal(object)        # After stop
    interrupted = pyqtSignal(object)    # After interruption
    waiting = pyqtSignal(object)        # When waiting

    on_play = pyqtSignal(object)        # Before play
    on_stop = pyqtSignal(object)        # Before stop
    on_pause = pyqtSignal(object)       # Before pause

    eos = pyqtSignal(object)                # End-of-Stream
    error = pyqtSignal(object, str, str)    # Emits error and details
    duration = pyqtSignal(object, int)      # The media duration is available
    media_updated = pyqtSignal(object)      # After media properties update

    state = NONE  # current media state

    def __init__(self, **kwsd):
        super().__init__(**kwsd)

    @abstractmethod
    def current_time(self):
        '''Returns the current playback time or -1 if not available'''
        return -1

    @abstractmethod
    def element(self, name):
        '''Returns the element with the specified name or None'''
        return None

    @abstractmethod
    def elements(self):
        '''Returns a list with all the MediaElement(s)'''
        return []

    @abstractmethod
    def elements_properties(self):
        '''Returns the elements configuration (dict)'''
        return {}

    def finalize(self):
        '''Finalize the media object'''

    @abstractmethod
    def input_uri(self):
        '''Returns the media input uri (e.g. "file:///home/..."), or None'''
        return None

    @abstractmethod
    def interrupt(self):
        '''
            Stop the playback without effects, go in STOPPED state
            and emit the interrupted signal
        '''

    @abstractmethod
    def pause(self, emit=True):
        '''The media go in PAUSED state and pause the playback'''

    @abstractmethod
    def play(self, emit=True):
        '''The media go in PLAYING state and starts the playback'''

    @abstractmethod
    def properties(self):
        '''Returns media property (dict)'''
        return {}

    @abstractmethod
    def seek(self, position, emit=True):
        '''Seek to "position"'''

    @abstractmethod
    def stop(self, emit=True):
        '''The media go in STOPPED state and stop the playback'''

    @abstractmethod
    def update_elements(self, conf, emit=True):
        '''Update the elements configuration'''

    @abstractmethod
    def update_properties(self, conf, emit=True):
        '''Update the media (and elements) configuration'''

    def __getitem__(self, key):
        return self.properties()[key]

    def __setitem__(self, key, value):
        self.properties()[key] = value
