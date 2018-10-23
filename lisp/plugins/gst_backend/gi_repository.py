"""Utility module for importing and checking gi.repository packages once"""

# "Solution" for https://bugzilla.gnome.org/show_bug.cgi?id=736260

import sys

sys.modules["gi.overrides.Gst"] = None
sys.modules["gi.overrides.GstPbutils"] = None

import gi

gi.require_version("Gst", "1.0")
gi.require_version("GstPbutils", "1.0")
gi.require_version("GstApp", "1.0")

# noinspection PyUnresolvedReferences
from gi.repository import Gst, GstPbutils, GObject, GstApp
