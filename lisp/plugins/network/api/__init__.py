import logging
from os import path

from lisp.core.loading import ModulesLoader
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


def route_all(app, api):
    for name, module in ModulesLoader(__package__, path.dirname(__file__)):
        for endpoint in getattr(module, "__endpoints__", ()):
            api.add_route(endpoint.UriTemplate, endpoint(app))
            logger.debug(
                translate("NetworkApiDebug", "New end-point: {}").format(
                    endpoint.UriTemplate
                )
            )
