"""Utility module for importing and checking gi.repository packages once"""

import gi

gi.require_version("Gst", "1.0")
gi.require_version("GstController", "1.0")
gi.require_version("GstPbutils", "1.0")
gi.require_version("GstApp", "1.0")

# noinspection PyUnresolvedReferences
# pylint: disable=unused-import
from gi.repository import GObject, Gst, GstController, GstPbutils, GstApp
