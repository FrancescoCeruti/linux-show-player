from collections import OrderedDict

from lisp.layouts.cart_layout.layout import CartLayout
from lisp.layouts.list_layout.layout import ListLayout


__LAYOUTS__ = OrderedDict({
    CartLayout.__name__: CartLayout,
    ListLayout.__name__: ListLayout
})


def get_layouts():
    return list(__LAYOUTS__.values())


def get_layout(class_name):
    return __LAYOUTS__[class_name]
