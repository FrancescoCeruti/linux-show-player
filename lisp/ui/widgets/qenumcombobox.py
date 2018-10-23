from PyQt5.QtWidgets import QComboBox
from enum import Enum


class QEnumComboBox(QComboBox):
    class Mode(Enum):
        Enum = 0
        Value = 1
        Name = 2

    def __init__(self, enum, items=(), mode=Mode.Enum, trItem=str, **kwargs):
        super().__init__(**kwargs)
        self.enum = enum
        self.mode = mode
        self.trItem = trItem

        self.setItems(items if items else enum)

    def setItems(self, items):
        self.clear()

        for item in items:
            if self.mode is QEnumComboBox.Mode.Value:
                value = item.value
            elif self.mode is QEnumComboBox.Mode.Name:
                value = item.name
            else:
                value = item

            self.addItem(self.trItem(item), value)

    def currentItem(self):
        return self.currentData()

    def setCurrentItem(self, item):
        try:
            if self.mode is QEnumComboBox.Mode.Value:
                item = self.enum(item)
            elif self.mode is QEnumComboBox.Mode.Name:
                item = self.enum[item]

            self.setCurrentText(self.trItem(item))
        except (ValueError, KeyError):
            pass
