from lisp.layouts.cart_layout.layout import CartLayout
from lisp.layouts.list_layout.layout import ListLayout


__LAYOUTS__ = [CartLayout, ListLayout]


def get_layouts():
    return __LAYOUTS__


def get_layout(name):
    for layout in __LAYOUTS__:
        if layout.NAME == name:
            return layout
