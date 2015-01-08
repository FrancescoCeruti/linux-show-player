##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################


class ActionCueFactory:

    __REGISTRY = {}

    @classmethod
    def create_cue(cls, options):
        type_ = options['type']
        cues = cls.__REGISTRY

        if type_ in cues:
            options['type'] = type_
            cue = cues[type_]()
            cue.update_properties(options)
            return cue

    @classmethod
    def register_action_cue(cls, cue_class):
        cls.__REGISTRY[cue_class.__name__] = cue_class
