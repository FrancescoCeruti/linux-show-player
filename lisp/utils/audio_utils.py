#########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
#########################################

import math
from urllib.request import quote, unquote
import wave

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GstPbutils


# Linear value for -100dB
MIN_dB = 0.000000312


def db_to_linear(value):
    '''dB value to linear value conversion.'''
    return math.pow(10, value / 20)


def linear_to_db(value):
    '''Linear value to dB value conversion.'''
    return 20 * math.log10(value) if value > MIN_dB else -100


def wave_duration(path):
    '''Get wave file duration using the standard wave library.'''
    try:
        with wave.open(path, 'r') as wfile:
            frames = wfile.getnframes()
            rate = wfile.getframerate()
            return int((frames / float(rate)) * 1000)
    except Exception:
        return -1


def uri_duration(uri):
    '''Get media file duration.'''
    duration = -1
    try:
        protocol, path = uri.split("://")
        # If a WAVE local file, then use the python wave module
        if protocol == "file":
            if path.lower().endswith(".wav") or path.lower().endswith(".wave"):
                duration = wave_duration(unquote(path))
        # Otherwise use GStreamer discovering (or when the first is failed)
        if duration <= 0:
            duration = uri_metadata(uri).get_duration() // Gst.MSECOND
    finally:
        return duration


def uri_metadata(uri):
    '''Discover media-file metadata using GStreamer.'''
    discoverer = GstPbutils.Discoverer()

    uri = uri.split("://")
    info = discoverer.discover_uri(uri[0] + "://" + quote(unquote(uri[1])))

    return info


def uri_tags(uri):
    '''Return a dict contings media metadata/tags.'''
    info = uri_metadata(uri)
    return parse_gst_tag_list(info.get_tags())


# Adaption of the code found in https://github.com/ch3pjw/pyam
def parse_gst_tag_list(gst_tag_list):
    '''Takes a GstTagList object and returns a dict.'''
    parsed_tags = {}

    def parse_tag(gst_tag_list, tag_name, parsed_tags):
        parsed_tags[tag_name] = gst_tag_list.get_value_index(tag_name, 0)

    gst_tag_list.foreach(parse_tag, parsed_tags)
    return parsed_tags
