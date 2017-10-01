import logging

from .api import API


def load_api(app):
    from . import cues
    from . import layout

    load_module(cues, app)
    load_module(layout, app)


def load_module(mod, app):
    for cls in mod.API_EXPORT:
        cls.route_to_app(app)

        logging.debug(
            'REMOTE2: Routed {} at {}'.format(cls.__name__, cls.UriTemplate))
