# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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

from lisp.backends.base.media_element import MediaElement


class GstMediaElement(MediaElement):
    """All the subclass must take the pipeline as __init__ argument"""

    def interrupt(self):
        """Called before Media interrupt"""

    def stop(self):
        """Called before Media stop"""

    def pause(self):
        """Called before Media pause"""

    def dispose(self):
        """Clean up the element"""

    def sink(self):
        """Return the GstElement used as sink"""
        return None

    def src(self):
        """Return the GstElement used as src"""
        return None

    def input_uri(self):
        """Input element should return the input uri"""
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
