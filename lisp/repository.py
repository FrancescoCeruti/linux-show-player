'''Utility module for importing and checking gi.repository packages once'''

import gi
gi.require_version('Gst', '1.0')

from gi.repository import Gst, GstPbutils, GObject  # @UnusedImport
