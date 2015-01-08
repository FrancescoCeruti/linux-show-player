##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from abc import ABCMeta

from PyQt5.QtCore import pyqtWrapperType

from lisp.core.qmeta import QABCMeta


class Singleton(type):

    __instance = None

    def __call__(cls, *args, **kwargs):  # @NoSelf
        if cls.__instance is not None:
            return cls.__instance
        else:
            cls.__instance = super(Singleton, cls).__call__(*args, **kwargs)
            return cls.__instance


class ABCSingleton(ABCMeta):

    __instance = None

    def __call__(cls, *args, **kwargs):  # @NoSelf
        if cls.__instance is not None:
            return cls.__instance
        else:
            cls.__instance = super(ABCSingleton, cls).__call__(*args, **kwargs)
            return cls.__instance


class QSingleton(pyqtWrapperType):

    def __call__(cls, *args, **kwargs):  # @NoSelf
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(QSingleton, cls).__call__(*args, **kwargs)
            return cls.__instance


class QABCSingleton(QABCMeta):

    __instance = None

    def __call__(cls, *args, **kwargs):  # @NoSelf
        if cls.__instance is not None:
            return cls.__instance
        else:
            cls.__instance = super(QABCSingleton, cls).__call__(*args,
                                                                **kwargs)
            return cls.__instance
