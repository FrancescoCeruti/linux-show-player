from lisp.core.configuration import config

if config['Backend']['Default'].lower() == 'gst':
    from .gst_backend import GstBackend
