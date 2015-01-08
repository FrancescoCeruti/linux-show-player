import logging
import os
import traceback

from lisp.utils.dyamic_loader import load_classes


# Use a set() for avoiding duplication
__SECTIONS = set()


def load():
    for name, section in load_classes(os.path.dirname(__file__),
                                         suffixes=['Settings']):

        if hasattr(section, 'initialize'):
            try:
                section.initialize()
            except Exception:
                logging.error('Error during ' + name + ' initialization')
                logging.debug(traceback.format_exc())
                continue

        # Add the new section in the global set
        __SECTIONS.add(section)


def sections():
    return list(__SECTIONS)


def sections_by_element_name():
    return dict([(s.ELEMENT.Name, s) for s in __SECTIONS])
