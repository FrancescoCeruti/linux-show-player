##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from lisp.gst.gst_element import GstMediaElement
from lisp.repository import Gst


class AutoSrc(GstMediaElement):

    Type = GstMediaElement.TYPE_INPUT
    Name = "AutoSrc"

    def __init__(self, pipe):
        super().__init__()

        self._src = Gst.ElementFactory.make("autoaudiosrc", "src")
        pipe.add(self._src)

    def src(self):
        return self._src
