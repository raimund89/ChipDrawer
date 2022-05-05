from PyQt6.QtGui import QBrush


class CDMaterial:
    def __init__(self, name, color, description):
        self._display_color = color
        self._name = name
        self._description = description

    @property
    def displayColor(self):
        return self._display_color

    @displayColor.setter
    def displayColor(self, c):
        self._display_color = c

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    def getBrush(self):
        return QBrush(self._display_color)
