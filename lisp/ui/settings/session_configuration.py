# This file is part of Linux Show Player
#
# Copyright 2022 Francesco Ceruti <ceppofrancy@gmail.com>
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

from collections import namedtuple

from lisp.core.dicttree import DictNode
from lisp.ui.settings.configuration_dialog import ConfigurationDialog
from lisp.ui.ui_utils import translate

PageEntry = namedtuple("PageEntry", ("page", "plugin"))


class SessionConfigurationDialog(ConfigurationDialog):
    PagesRegistry = DictNode()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowTitle(translate('SessionConfiguration', 'Session preferences'))

    @staticmethod
    def _getConfigFromPageEntry(page_parent):
        return page_parent.value.plugin.SessionConfig

    @classmethod
    def registerSettingsPage(cls, path, page, plugin):
        """
        :param path: indicate the page "position": 'category.sub.key'
        :type path: str
        :type page: type
        :type plugin: lisp.core.plugin.Plugin
        """
        cls.PagesRegistry.set(
            path, PageEntry(page=page, plugin=plugin)
        )
