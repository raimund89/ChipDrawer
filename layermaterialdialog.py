from PyQt6 import uic
from PyQt6.QtGui import QCloseEvent, QPixmap, QIcon
from PyQt6.QtWidgets import QDialog


def icon_from_color(c):
    pm = QPixmap(100, 100)
    pm.fill(c)
    return QIcon(pm)


class LayerMaterialDialog(QDialog):
    def __init__(self, parent, mat):
        super().__init__(parent)

        # loading the ui file with uic module
        uic.loadUi("layouts/layermaterial.ui", self)

        index = 0

        for i, material in enumerate(parent.theme.materials()):
            self.material.addItem(icon_from_color(material.displayColor), material.name)

            if mat.name == material.name:
                index = i

        self.material.setCurrentIndex(index)

        self.show()

    def closeEvent(self, event: QCloseEvent) -> None:
        print("Closing")
