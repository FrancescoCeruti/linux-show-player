##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from abc import ABCMeta

from PyQt5.QtCore import pyqtWrapperType


class QABCMeta(pyqtWrapperType, ABCMeta):
    pass
