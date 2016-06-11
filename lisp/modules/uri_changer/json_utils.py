# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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


def json_deep_search(iterable, field):
    """Takes a JSON like data-structure and search for the occurrences
    of the given field/key.
    """
    fields_found = []

    if isinstance(iterable, dict):
        for key, value in iterable.items():
            if key == field:
                fields_found.append(value)

            elif isinstance(value, (dict, list)):
                fields_found.extend(json_deep_search(value, field))

    elif isinstance(iterable, list):
        for item in iterable:
            fields_found.extend(json_deep_search(item, field))

    return fields_found


def json_deep_replace(iterable, field, replace_function):
    """Takes a JSON like data-structure and replace the value for all the
    occurrences of the given field/key with the given replace-function.
    """
    if isinstance(iterable, dict):
        for key, value in iterable.items():
            if key == field:
                iterable[key] = replace_function(value)

            elif isinstance(value, (dict, list)):
                json_deep_replace(value, field, replace_function)

    elif isinstance(iterable, list):
        for item in iterable:
            json_deep_replace(item, field, replace_function)
