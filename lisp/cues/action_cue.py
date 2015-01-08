##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from lisp.cues.cue import Cue


class ActionCue(Cue):
    '''Action cues should inherit from this class.'''

    def __init__(self, **kwds):
        super().__init__(**kwds)
