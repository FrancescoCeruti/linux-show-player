##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################


class CueFactory:
    '''
        The "CueFactory" class provide a unified abstract-factory for build
        different cues types across the application.

        All the capabilities must be register, via concrete-factory.
    '''

    __REGISTRY = {}

    # Register methods

    @classmethod
    def register_factory(cls, cue_type, factory):
            cls.__REGISTRY[cue_type] = factory

    @classmethod
    def unregister_cue(cls, cue_type):
        cls.__REGISTRY.pop(cue_type)

    # Create method

    @classmethod
    def create_cue(cls, options):
        factory = cls.__REGISTRY.get(options.get('type'))

        if factory is None:
            cuetype = options.get('type', 'Undefined')
            raise Exception('Cue not available: ' + str(cuetype))

        return factory.create_cue(options)

    @classmethod
    def create_cue_by_type(cls, cue_type):
        return cls.create_cue({'type': cue_type})

    @classmethod
    def clone_cue(cls, cue, same_id=False):
        if not same_id:
            conf = cue.properties().copy()
            conf.pop('id')
            return cls.create_cue(conf)
        else:
            return cls.create_cue(cue.properties())
