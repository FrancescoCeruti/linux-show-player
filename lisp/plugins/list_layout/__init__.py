from lisp.core.plugin import Plugin
from lisp.layout import register_layout
from lisp.plugins.list_layout.settings import ListLayoutSettings
from lisp.plugins.list_layout.layout import ListLayout as _ListLayout
from lisp.ui.settings.app_configuration import AppConfigurationDialog


class ListLayout(Plugin):
    Name = "List Layout"
    Description = "Provide a layout that organize the cues in a list"
    Authors = ("Francesco Ceruti",)

    def __init__(self, app):
        super().__init__(app)

        _ListLayout.Config = ListLayout.Config
        register_layout(_ListLayout)
        AppConfigurationDialog.registerSettingsPage(
            "layouts.list_layout", ListLayoutSettings, ListLayout.Config
        )
