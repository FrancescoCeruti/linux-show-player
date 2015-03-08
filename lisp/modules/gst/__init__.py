##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from lisp.repository import Gst, GObject
from lisp.gst import elements
from lisp.gst import settings
from lisp.utils.configuration import config

from lisp.cues.cue_factory import CueFactory
from lisp.gst.gst_media_cue import GstMediaCueFactory, GstMediaCue
from lisp.gst.gst_media_settings import GstMediaSettings
from lisp.gst.gst_preferences import GstPreferences
from lisp.layouts.cue_layout import CueLayout
from lisp.ui.settings.app_settings import AppSettings


def initialize():
    # Init GStreamer and GObject
    GObject.threads_init()
    Gst.init(None)

    # Register GStreamer settings widgets
    AppSettings.register_settings_widget(GstPreferences)
    # Register the GstMedia cue builder
    CueFactory.register_factory(config['Gst']['CueType'], GstMediaCueFactory)
    # Add MediaCue settings widget to the CueLayout
    CueLayout.add_settings_section(GstMediaSettings, GstMediaCue)

    elements.load()
    settings.load()


def terminate():
    pass
