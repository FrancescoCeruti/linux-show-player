##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from lisp.cues.media_cue import MediaCue
from lisp.gst.gst_media import GstMedia


class GstMediaCue(MediaCue):
    pass


class GstMediaCueFactory:

    @classmethod
    def create_cue(self, options):
        cue = GstMediaCue(GstMedia())
        cue.update_properties(options)

        return cue
