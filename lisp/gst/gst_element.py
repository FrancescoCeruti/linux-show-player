##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from lisp.core.media_element import MediaElement


class GstMediaElement(MediaElement):
    '''All the subclass must take the pipeline as __init__ argument'''

    def interrupt(self):
        '''Called before Media interrupt'''

    def stop(self):
        '''Called before Media stop'''

    def pause(self):
        '''Called before Media pause'''

    def dispose(self):
        '''Called after element remotion'''

    def sink(self):
        '''Return the GstElement used as sink'''
        return None

    def src(self):
        '''Return the GstElement used as src'''
        return None

    def input_uri(self):
        '''Input element should return the input uri'''
        return None

    def link(self, element):
        if self.src() is not None:
            sink = element.sink()
            if sink is not None:
                return self.src().link(sink)
        return False

    def unlink(self, element):
        if self.src() is not None:
            sink = element.sink()
            if sink is not None:
                return self.src().unlink(sink)
        return False
