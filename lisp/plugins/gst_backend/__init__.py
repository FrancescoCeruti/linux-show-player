from lisp.core.configuration import AppConfig

if AppConfig()['Backend']['Default'].lower() == 'gst':
    from .gst_backend import GstBackend
