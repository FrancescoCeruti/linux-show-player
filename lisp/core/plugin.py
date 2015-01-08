##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################


class Plugin:

    # Plugin name
    Name = 'NoName'

    def reset(self):
        ''' Reset the plugin '''

    def get_settings(self):
        '''
            If implemented, it must return the plugin settings as dict.
            For example: {'trigger': 'play', 'action': callable}
        '''
        return {}

    def load_settings(self, conf):
        '''Load the settings in the same form of get_settings() return value'''
