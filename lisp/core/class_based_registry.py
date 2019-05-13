# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
#
# Linux Show Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linux Show Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>.


class ClassBasedRegistry:
    """Allow to register/un-register and filter items using a reference class.

    The filter "check" whenever the filter-class is a subclass of
    the one used to register the item or exactly the the same.

    .. highlight::

        reg = ClassBasedRegistry()
        reg.add('Object-Item', object)
        reg.add('List-Item', list)

        list(reg.filter(object))  # ['Object-Item', 'List-Item']
        list(reg.filter(list))    # ['List-Item']
    """

    def __init__(self):
        self._registry = {}

    def add(self, item, ref_class=object):
        """Register a item for ref_class."""
        if ref_class not in self._registry:
            self._registry[ref_class] = [item]
        elif item not in self._registry[ref_class]:
            self._registry[ref_class].append(item)

    def remove(self, item):
        """Remove all the occurrences of the given item."""
        for ref_class in self._registry:
            try:
                self._registry[ref_class].remove(item)
            except ValueError:
                pass

    def filter(self, ref_class=object):
        """Return an iterator over items registered with ref_class
        or subclasses.

        The items are sorted by ref_class name.
        """
        for class_ in self._registry.keys():
            if issubclass(ref_class, class_):
                yield from self._registry[class_]

    def clear_class(self, ref_class=object):
        """Remove all the items for ref_class."""
        self._registry[ref_class].clear()

    def ref_classes(self):
        """Return a view-like object of all the registered references."""
        return self._registry.keys()

    def clear(self):
        self._registry.clear()
