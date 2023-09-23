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

from os.path import dirname

from lisp.core.loading import load_classes

Protocols = []
CueSettingsPages = []
LayoutSettingsPages = []


def load():
    for _, protocol in load_classes(__package__, dirname(__file__)):
        Protocols.append(protocol)

        # Get settings pages
        if protocol.CueSettings is not None:
            CueSettingsPages.append(protocol.CueSettings)
        if protocol.LayoutSettings is not None:
            LayoutSettingsPages.append(protocol.LayoutSettings)
