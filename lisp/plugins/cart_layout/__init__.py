from lisp.core.plugin import Plugin
from lisp.layout import register_layout
from lisp.plugins.cart_layout.settings import CartLayoutSettings
from lisp.plugins.cart_layout.layout import CartLayout as _CartLayout
from lisp.ui.settings.app_configuration import AppConfigurationDialog


class CartLayout(Plugin):
    Name = "Cart Layout"
    Description = "Provide a layout that organizes cues in grid-like pages"
    Authors = ("Francesco Ceruti",)

    def __init__(self, app):
        super().__init__(app)

        _CartLayout.Config = CartLayout.Config
        register_layout(_CartLayout)
        AppConfigurationDialog.registerSettingsPage(
            "layouts.cart_layout", CartLayoutSettings, CartLayout.Config
        )
