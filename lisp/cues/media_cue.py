##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################


from lisp.core.media import Media

from lisp.cues.cue import Cue
from lisp.utils.decorators import synchronized


class MediaCue(Cue):

    def __init__(self, media, cue_id=None):
        super().__init__(cue_id)

        self.media = media
        self.update_properties({'pause': False})

        self.__finalized = False

    @synchronized
    def execute(self, emit=True):
        super().execute(emit=emit)

        if self.media.state != Media.PLAYING:
            self.media.play()
        elif self['pause']:
            self.media.pause()
        else:
            self.media.stop()

    def properties(self):
        properties = super().properties().copy()
        properties['media'] = self.media.properties()
        return properties

    def update_properties(self, properties):
        if 'media' in properties:
            media_props = properties.pop('media')
            self.media.update_properties(media_props)

        super().update_properties(properties)

    def finalize(self):
        if not self.__finalized:
            self.__finalized = True
            self.media.dispose()

    def is_finalized(self):
        return self.__finalized
