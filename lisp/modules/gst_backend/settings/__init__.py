import logging
import os
import traceback

from lisp.utils.dyamic_loader import ClassesLoader

# Use a set() for avoiding duplication
__PAGES = set()


def load():
    for name, page in ClassesLoader(os.path.dirname(__file__),
                                    suffixes=('Settings', )):

        if hasattr(page, 'initialize'):
            try:
                page.initialize()
            except Exception:
                logging.error('Error during ' + name + ' initialization')
                logging.debug(traceback.format_exc())
                continue

        __PAGES.add(page)


def pages():
    return list(__PAGES)


def pages_by_element():
    return {s.ELEMENT.__name__: s for s in __PAGES}
