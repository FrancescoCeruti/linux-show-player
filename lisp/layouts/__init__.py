from lisp.layouts.cart_layout.layout import CartLayout
from lisp.layouts.list_layout.layout import ListLayout


__LAYOUTS__ = {
    CartLayout.__name__: CartLayout,
    ListLayout.__name__: ListLayout
}


def get_layouts():
    return sorted(__LAYOUTS__.values())


def get_layout(class_name):
    return __LAYOUTS__[class_name]
