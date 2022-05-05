import os

from PyQt6 import uic
from PyQt6.QtCore import QModelIndex, pyqtSlot
from PyQt6.QtGui import QCloseEvent, QUndoStack
from PyQt6.QtWidgets import QMainWindow, QMessageBox

from CDItemDelegate import CDItemDelegate
from buildingblocks import CDBuildingBlockList


class MainWindow(QMainWindow):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings

        # loading the ui file with uic module
        uic.loadUi("layouts/mainwindow.ui", self)

        self.blocks = CDBuildingBlockList(self, os.path.dirname(self.settings.fileName()))

        # Create the undo stack and add the undo/redo actions
        self.undostack = QUndoStack(self)
        undo = self.undostack.createUndoAction(self)
        undo.setShortcut('Ctrl+Z')
        redo = self.undostack.createRedoAction(self)
        redo.setShortcut('Ctrl+Y')
        self.menu_Edit.insertAction(self.menu_Edit.actions()[0], undo)
        self.menu_Edit.insertAction(self.menu_Edit.actions()[1], redo)

        # Pass the undostack on to the project
        self.drawing_area.setUndoStack(self.undostack)

        self.btn_add_layer.setProperty('class', 'success')
        self.btn_remove_layer.setProperty('class', 'danger')

        self.layer_list.setItemDelegate(CDItemDelegate(self.layer_list))

        self.layer_list.setModel(self.drawing_area.layer_model)

        self.drawing_area.initEmptyScene()
        self.drawing_area.setActiveLayer(0)

        self.showMaximized()

    @pyqtSlot()
    def signal_add_layer(self):
        pass

    @pyqtSlot()
    def signal_remove_layer(self):
        pass

    @pyqtSlot(QModelIndex)
    def signal_layer_clicked(self, index):
        pass

    @pyqtSlot()
    def signal_show_3d(self):
        pass

    @pyqtSlot()
    def signal_save(self):
        pass

    @pyqtSlot()
    def signal_export(self):
        pass

    @pyqtSlot()
    def signal_open(self):
        pass

    @pyqtSlot()
    def signal_new(self):
        self.drawing_area.project_new()

        self.drawing_area.initEmptyScene()
        self.drawing_area.setActiveLayer(0)

    def closeEvent(self, event: QCloseEvent) -> None:
        # TODO: Replace this entire thingy with a) checking if anything needs to be saved and b) then closing everything
        d = QMessageBox.question(self, "Chip Drawer", "Are you sure you want to exit?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if d != QMessageBox.StandardButton.Yes:
            event.ignore()
        else:
            event.accept()
