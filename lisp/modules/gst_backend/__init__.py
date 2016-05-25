from lisp.utils.configuration import config

if config['Backend']['Default'].lower() == 'gst':
    from .gst_backend import GstBackend
