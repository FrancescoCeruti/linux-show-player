##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################


class MediaElement:

    TYPE_INPUT = 0
    TYPE_OUTPUT = 1
    TYPE_PLUGIN = 2

    # Type of the element
    Type = None
    # Name of the element
    Name = ''
    # Id of the element instance
    Id = ''

    def set_property(self, name, value):
        '''Set the given property'''

    def properties(self):
        '''Return the properties in a dict'''
        return {}

    def update_properties(self, properties):
        for key in properties:
            self.set_property(key, properties[key])
