from PyQt6 import uic
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QDialog


# TODO: Merge this dialog with the widget shown in the lower-left corner of the screen. Basically, make it a widget.

def icon_from_color(c):
    pm = QPixmap(100, 100)
    pm.fill(c)
    return QIcon(pm)


class NewLayerDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        # loading the ui file with uic module
        uic.loadUi("layouts/newlayer.ui", self)

        # Load current layers
        for layer in parent.chip_layers:
            self.insert_after.addItem(layer.name)

        for material in parent.theme.materials():
            self.material.addItem(icon_from_color(material.displayColor), material.name)
            self.background_material.addItem(icon_from_color(material.displayColor), material.name)

        self.material.setCurrentIndex(parent.theme.default_material)
        self.background_material.setCurrentIndex(parent.theme.default_background)

        self.show()

    def accept(self) -> None:
        if len(self.layer_name.text()) > 0:
            super().accept()
