##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from collections import Mapping
from itertools import chain
from os import listdir, path
from os.path import isdir, exists, join

from lisp.repository import Gst


def deep_update(d, u):
    '''Update recursively d with u'''
    for k in u:
        if isinstance(u[k], Mapping):
            d[k] = deep_update(d.get(k, {}), u[k])
        else:
            d[k] = u[k]
    return d


def json_deep_search(iterable, field):
    '''
        Takes a JSON like data-structure and search for the occurrences
        of the given field/key.
    '''
    fields_found = []

    if isinstance(iterable, dict):
        for key, value in iterable.items():
            if key == field:
                fields_found.append(value)

            elif isinstance(value, dict) or isinstance(value, list):
                fields_found.extend(json_deep_search(value, field))

    elif isinstance(iterable, list):
        for item in iterable:
            fields_found.extend(json_deep_search(item, field))

    return fields_found


def json_deep_replace(iterable, field, replace_function):
    '''
        Takes a JSON like data-structure and replace the value for the
        occurrences of the given field/key with the given replace-function.
    '''
    if isinstance(iterable, dict):
        for key, value in iterable.items():
            if key == field:
                iterable[key] = replace_function(value)

            elif isinstance(value, dict) or isinstance(value, list):
                json_deep_replace(value, field, replace_function)

    elif isinstance(iterable, list):
        for item in iterable:
            json_deep_replace(item, field, replace_function)


def gst_file_extensions(mimetypes):
    '''
        Get all the file extension available via GStreamer API.

        The mimetypes given as categories need only partial matching
        (e.g. 'audio/x-raw' can be 'audio' or 'x-raw' or 'io/x' etc ...).
        If no mimetype match the extension will be appended in 'other', that
        was always included in the result.

        :param mimietypes: mimetypes for splitting categories
        :type mimetypes: list

        :return: A dict {'mime0': [ext0, ext1], ... , 'other': [extX, extY]}
    '''
    extensions = {}

    for mimetype in mimetypes + ['others']:
        extensions[mimetype] = []

    for gtff in Gst.TypeFindFactory.get_list():
        caps = gtff.get_caps()

        if caps is not None:
            for i in range(caps.get_size()):
                mime = caps.get_structure(i).to_string()
                for mimetype in mimetypes:
                    if mimetype in mime:
                        extensions[mimetype].extend(gtff.get_extensions())
                    else:
                        extensions['others'].extend(gtff.get_extensions())

    return extensions


def file_filters_from_exts(extensions, allexts=True, anyfile=True):
    ''' Create a filter-string, for a QFileChooser '''
    filters = []

    for key in extensions:
        filters.append(key + ' (' + ' *.'.join(extensions[key]) + ')')

    filters.sort()

    if allexts:
        filters.insert(0, 'All supported (' +
                       ' *.'.join(chain(*extensions.values())) + ')')
    if anyfile:
        filters.append('Any file (*)')

    return ';;'.join(filters)


def file_path(base, filename):
    return path.abspath(path.join(path.dirname(base), filename))


def find_packages(path='.'):
    ''' List the python packages in the given directory '''

    return [d for d in listdir(path) if isdir(join(path, d)) and
            exists(join(path, d, '__init__.py'))]


def time_tuple(millis):
    ''' millis is an integer number of milliseconds '''
    seconds, millis = divmod(millis, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    return (hours, minutes, seconds, millis)


def strtime(time, accurate=False):
    '''
        Return a string from the given milliseconds time:
        - hh:mm:ss when > 59min
        - mm:ss:00 when < 1h and accurate=False
        - mm:ss:z0 when < 1h and accurate=True
    '''
    time = time_tuple(time)
    if time[0] > 0:
        return'%02d:%02d:%02d' % time[:-1]
    elif accurate:
        time = time[1:3] + (time[3] // 100,)
        return '%02d:%02d:%01d' % time + '0'
    else:
        return '%02d:%02d' % time[1:3] + ':00'
