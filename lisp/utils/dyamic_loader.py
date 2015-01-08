##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import logging
import pkgutil
import traceback


class load_classes:
    '''
        Generator for iterating over classes in package.

        The class name must be the same as the module name, optionally
        suffixes and prefixes lists can be provided.

        Example:

        elements_package
        |__element1.py
        |  |__Element1
        |__element_extra.py
           |__ElementExtra
    '''

    def __init__(self, package_path, prefixes=[''], suffixes=['']):
        self._package_path = package_path
        self._prefixes = prefixes
        self._suffixes = suffixes

    def __iter__(self):
        return self.load()

    def load(self):
        ''' Generate lists of tuples (class-name, class-object) '''
        modules = pkgutil.iter_modules(path=[self._package_path])

        for loader, mod_name, _ in modules:
            # Import module
            module = loader.find_module(mod_name).load_module(mod_name)

            # Load class from imported module
            partial = []
            for prefix, suffix in zip(self._prefixes, self._suffixes):
                try:
                    name = class_name_from_module(mod_name, prefix, suffix)
                    cls = getattr(module, name)
                    partial.append((name, cls))
                except Exception:
                    logging.error('Error during module loading: ' + mod_name)
                    logging.debug(traceback.format_exc())

            # Yield the class name and the class-object
            if len(partial) == 1:
                yield partial[0]
            elif len(partial) > 0:
                yield partial


def class_name_from_module(mod_name, pre='', suf=''):
    '''
        Return the class name for a dynamic loaded module
        If the name is module_name, the result will be ModuleName

        :param pre: prefix for the class name (default '')
        :param suf: suffix for the class name (default '')
    '''

    # Capitalize the first letter of each word
    base_name = ''.join([word.title() for word in mod_name.split('_')])
    # Add prefix and suffix to the base name
    return pre + base_name + suf
