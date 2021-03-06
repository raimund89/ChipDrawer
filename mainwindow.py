import os

from PyQt6 import uic
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QCloseEvent, QUndoStack
from PyQt6.QtWidgets import QMainWindow, QMessageBox

from CDItemDelegate import CDItemDelegate
from buildingblocks import CDBuildingBlockList
from cd3dviewer import CD3DViewer


# TODO: Implement recents


class MainWindow(QMainWindow):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings

        self.viewer3d = None

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
        self.undostack.cleanChanged.connect(self.project_clean_changed)
        self.undostack.indexChanged.connect(self.project_index_changed)

        # Pass the undostack on to the project
        self.drawing_area.setUndoStack(self.undostack)

        self.btn_add_layer.setProperty('class', 'success')
        self.btn_remove_layer.setProperty('class', 'danger')

        self.layer_list.setItemDelegate(CDItemDelegate(self.layer_list))

        self.layer_list.setModel(self.drawing_area.layer_model)

        self.drawing_area.project_new()
        self.undostack.cleanChanged.emit(False)

        self.showMaximized()

    @pyqtSlot()
    def signal_show_3d(self):
        if not self.viewer3d:
            self.viewer3d = CD3DViewer(self, project=self.drawing_area)

    @pyqtSlot()
    def signal_save(self):
        self.drawing_area.project_save()

    @pyqtSlot()
    def signal_save_as(self):
        self.drawing_area.project_save(saveas=True)

    @pyqtSlot()
    def signal_export(self):
        self.drawing_area.project_save(export=True)

    @pyqtSlot()
    def signal_open(self):
        if not self.undostack.isClean():
            # The current project is not saved
            d = QMessageBox.question(self, "Chip Drawer", "Do you want to save the project before closing it?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)

            if d == QMessageBox.StandardButton.Yes:
                # We want to save
                if not self.drawing_area.project_save():
                    # In case saving was cancelled
                    return
            elif d == QMessageBox.StandardButton.Cancel:
                # We don't want to leave the project
                return

        self.drawing_area.project_open()

    @pyqtSlot()
    def signal_new(self):
        if not self.undostack.isClean():
            # The current project is not saved
            d = QMessageBox.question(self, "Chip Drawer", "Do you want to save the project before closing it?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)

            if d == QMessageBox.StandardButton.Yes:
                # We want to save
                if not self.drawing_area.project_save():
                    # In case saving was cancelled
                    return
            elif d == QMessageBox.StandardButton.Cancel:
                # We don't want to leave the project
                return

        # In case we either saved successfully, or don't want to save: start a new project
        self.drawing_area.project_new()

    def closeEvent(self, event: QCloseEvent) -> None:
        if not self.undostack.isClean():
            # The current project is not saved
            d = QMessageBox.question(self, "Chip Drawer", "Do you want to save the project before closing it?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)

            if d == QMessageBox.StandardButton.Yes:
                # We want to save
                if not self.drawing_area.project_save():
                    # In case saving was cancelled
                    event.ignore()
                    return
            elif d == QMessageBox.StandardButton.Cancel:
                # We don't want to leave the project
                event.ignore()
                return

        event.accept()

    @pyqtSlot(bool)
    def project_clean_changed(self, clean):
        self.setWindowTitle(
            f"Chip Drawer - {self.drawing_area.filename if self.drawing_area.filename else 'Untitled'}{'' if clean else '*'}")

    @pyqtSlot(int)
    def project_index_changed(self, index):
        if self.viewer3d:
            self.viewer3d.updateChip()
