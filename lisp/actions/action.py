##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################


class Action():

    def properties(self):
        return {}

    def do(self):
        pass

    def undo(self):
        pass

    def redo(self):
        pass

    def log(self):
        return ''

    def update_properties(self, props):
        self.properties().update(props)

    def __getitem__(self, key):
        return self.properties()[key]

    def __setitem__(self, key, value):
        self.properties()[key] = value
