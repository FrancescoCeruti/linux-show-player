# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
#
# Linux Show Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linux Show Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>.

from lisp.core.model import Model
from lisp.cues.cue import Cue, CueAction


class CueModel(Model):
    """Simple model to store cue(s), as (cue.id, cue) pairs.

    The model can be iterated to retrieve the cues, to get id-cue pairs
    use the items() function, to get only the id(s) use the keys() function.
    """

    def __init__(self):
        super().__init__()
        self.__cues = {}

    def add(self, cue):
        if cue.id in self.__cues:
            raise ValueError("the cue is already in the model")

        self.__cues[cue.id] = cue
        self.item_added.emit(cue)

    def remove(self, cue):
        self.pop(cue.id)

    def pop(self, cue_id):
        """:rtype: Cue"""
        cue = self.__cues.pop(cue_id)

        # Try to interrupt/stop the cue
        if CueAction.Interrupt in cue.CueActions:
            cue.interrupt()
        elif CueAction.Stop in cue.CueActions:
            cue.stop()

        self.item_removed.emit(cue)

        return cue

    def get(self, cue_id, default=None):
        """Return the cue with the given id, or the default value.

        :rtype: Cue
        """
        return self.__cues.get(cue_id, default)

    def items(self):
        """Return a set-like object proving a view on model items (id, cue)"""
        return self.__cues.items()

    def keys(self):
        """Return a set-like object proving a view on of model keys (cue id)"""
        return self.__cues.keys()

    def reset(self):
        self.__cues.clear()
        self.model_reset.emit()

    def filter(self, cue_class=Cue):
        """Return an iterator over cues that are instances of the given class"""
        for cue in self.__cues.values():
            if isinstance(cue, cue_class):
                yield cue

    def __iter__(self):
        return self.__cues.values().__iter__()

    def __len__(self):
        return len(self.__cues)

    def __contains__(self, cue):
        return cue.id in self.__cues
