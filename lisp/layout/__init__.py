__LAYOUTS__ = {}


def get_layouts():
    return list(__LAYOUTS__.values())


def get_layout(class_name):
    return __LAYOUTS__[class_name]


def register_layout(layout):
    __LAYOUTS__[layout.__name__] = layout
