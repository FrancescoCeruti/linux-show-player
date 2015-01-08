##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################


from PyQt5.QtWidgets import QMessageBox


class QDetailedMessageBox(QMessageBox):
    '''This class provide static methods for detailed message boxes'''

    @staticmethod
    def dcritical(title, text, detailed_text, parent=None):
        '''MessageBox with "Critical" icon'''
        QDetailedMessageBox.dgeneric(title,
                                     text,
                                     detailed_text,
                                     QMessageBox.Critical,
                                     parent)

    @staticmethod
    def dwarning(title, text, detailed_text, parent=None):
        '''MessageBox with "Warning" icon'''
        QDetailedMessageBox.dgeneric(title,
                                     text,
                                     detailed_text,
                                     QMessageBox.Warning,
                                     parent)

    @staticmethod
    def dinformation(title, text, detailed_text, parent=None):
        '''MessageBox with "Information" icon'''
        QDetailedMessageBox.dgeneric(title,
                                     text,
                                     detailed_text,
                                     QMessageBox.Information,
                                     parent)

    @staticmethod
    def dgeneric(title, text, detailed_text, icon, parent=None):
        '''Build and show a MessageBox whit detailed text'''
        messageBox = QMessageBox(parent)

        messageBox.setIcon(icon)
        messageBox.setDetailedText(detailed_text)
        messageBox.setWindowTitle(title)
        messageBox.setText(text)
        messageBox.addButton(QMessageBox.Ok)
        messageBox.setDefaultButton(QMessageBox.Ok)

        messageBox.exec_()
