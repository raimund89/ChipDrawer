import math
import os

from PyQt6.QtCore import QEvent, QModelIndex, Qt, pyqtSlot
from PyQt6.QtGui import QBrush, QEnterEvent, QIcon, QKeyEvent, QMouseEvent, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QApplication, QGraphicsRectItem, QGraphicsScene, QGraphicsView, \
    QMessageBox

from cdproject.commands import CDCommandAddLayer, CDCommandChangeChipHeight, CDCommandChangeChipMargins, \
    CDCommandChangeChipWidth, CDCommandItemAdd, CDCommandItemsMove, CDCommandLayerDown, CDCommandLayerMaterial, \
    CDCommandLayerName, \
    CDCommandLayerSubstrate, CDCommandLayerThickness, CDCommandLayerUp, CDCommandLayerVisibility, CDCommandRemoveLayer
from cdproject.layer import CDLayer
from cdproject.layer_model import LayerModel
from cdproject.theme import CDThemeList
from newlayerdialog import NewLayerDialog


def icon_from_color(c):
    pm = QPixmap(100, 100)
    pm.fill(c)
    return QIcon(pm)


class CDProject(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self.theme = None
        self.themelist = None
        self.chip_margin = None
        self.chip_height = None
        self.chip_width = None
        self.chip_layers = []
        self.selected_items_old_positions = []
        self.selection_moved = None
        self.selected_items = []
        self.snaplist = []
        self.floating_item = None
        self.zoom_total = None
        self.chip_outline = None
        self.background = None
        self.undostack = None

        self.layer_model = LayerModel(None, self)
        self._active_layer = -1

        self.verticalScrollBar().valueChanged.connect(self.recalcSnaps)
        self.horizontalScrollBar().valueChanged.connect(self.recalcSnaps)

    def initEmptyScene(self):
        # Add the first layer by default
        self.layer_model.beginResetModel()
        layer = CDLayer(self, "Layer 1")
        layer.setVisible(True)
        layer.substrate = True
        layer.material = self.theme.material(0)
        layer.setZValue(0)
        self.chip_layers.insert(0, layer)
        self.scene().addItem(layer)
        self.layer_model.endResetModel()

        # Hack to fix a Z-value issue: without these two lines, the Z-value of the first layer substrate is not
        # respected until the layers have been rearranged.
        layer.substrate = False
        layer.substrate = True

    def setActiveLayer(self, row=0):
        self.parent().parent().layer_list.clicked.emit(self.layer_model.index(row, 2))
        self.parent().parent().layer_list.setCurrentIndex(self.layer_model.index(row, 2))

    def setUndoStack(self, undostack):
        self.undostack = undostack

    def setOutlines(self):
        self.setSceneRect(-self.chip_margin,
                          -self.chip_margin,
                          self.chip_width + 2 * self.chip_margin,
                          self.chip_height + 2 * self.chip_margin)
        self.background.setRect(-self.chip_margin,
                                -self.chip_margin,
                                self.chip_width + 2 * self.chip_margin,
                                self.chip_height + 2 * self.chip_margin)
        self.chip_outline.setRect(0, 0, self.chip_width, self.chip_height)

        for layer in self.chip_layers:
            layer.resize_chip()

    @pyqtSlot()
    def signal_toolbox_clicked(self):
        block = self.sender().block
        if block:
            self.floating_item = block()
            self.floating_item.setZValue(1000)
            self.floating_item.setVisible(False)
            self.scene().addItem(self.floating_item)
        else:
            if self.floating_item:
                self.scene().removeItem(self.floating_item)
                self.floating_item = None

    ###########################################################################
    #                                                                         #
    #  Layer methods                                                          #
    #                                                                         #
    ###########################################################################

    @pyqtSlot()
    def signal_layer_add(self):
        dialog = NewLayerDialog(self)
        dialog.exec()
        if dialog.result():
            self.undostack.push(CDCommandAddLayer(project=self,
                                                  position=dialog.insert_after.currentIndex(),
                                                  name=dialog.layer_name.text(),
                                                  visible=dialog.check_visible.isChecked(),
                                                  substrate=dialog.check_substrate.isChecked(),
                                                  material=self.theme.material(dialog.material.currentIndex())
                                                  )
                                )

    @pyqtSlot()
    def signal_layer_remove(self):
        if self._active_layer == -1:
            return

        msg = QMessageBox(QMessageBox.Icon.Warning, "Remove Layer", "Are you sure you want to remove this layer?",
                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, self)

        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.undostack.push(CDCommandRemoveLayer(project=self, position=self._active_layer))

    @pyqtSlot(QModelIndex)
    def signal_layer_clicked(self, index):
        self._active_layer = index.row()

        self.parent().parent().btn_layer_up.setEnabled(self._active_layer > 0)
        self.parent().parent().btn_layer_down.setEnabled(self._active_layer < len(self.chip_layers) - 1)

        row = index.row()
        if row > -1:
            self.parent().parent().layer_prop_name.setText(self.chip_layers[row].name)
            self.parent().parent().layer_prop_material.setCurrentIndex(
                self.theme.material(self.chip_layers[row].material.name)[0])
            self.parent().parent().layer_prop_visible.setCheckState(
                Qt.CheckState.Checked if self.chip_layers[row].isVisible() else Qt.CheckState.Unchecked)
            self.parent().parent().layer_prop_substrate.setCheckState(
                Qt.CheckState.Checked if self.chip_layers[row].substrate else Qt.CheckState.Unchecked)
            self.parent().parent().layer_prop_thickness.setValue(self.chip_layers[row].thickness)
            self.parent().parent().layer_props.setEnabled(True)
        else:
            self.parent().parent().layer_prop_name.setText("")
            self.parent().parent().layer_prop_material.setCurrentIndex(0)
            self.parent().parent().layer_prop_visible.setCheckState(Qt.CheckState.Unchecked)
            self.parent().parent().layer_prop_substrate.setCheckState(Qt.CheckState.Unchecked)
            self.parent().parent().layer_prop_thickness.setValue(0.0)
            self.parent().parent().layer_props.setEnabled(False)

    @pyqtSlot(int)
    def signal_layer_changed_material(self, m):
        self.undostack.push(CDCommandLayerMaterial(self, self._active_layer, self.theme.material(m)))

    @pyqtSlot()
    def signal_layer_changed_name(self):
        self.undostack.push(CDCommandLayerName(self, self._active_layer, self.parent().parent().layer_prop_name.text()))

    @pyqtSlot(bool)
    def signal_layer_changed_visibility(self, v):
        self.undostack.push(CDCommandLayerVisibility(self, self._active_layer, v))

    @pyqtSlot(bool)
    def signal_layer_changed_substrate(self, s):
        self.undostack.push(CDCommandLayerSubstrate(self, self._active_layer, s))

    @pyqtSlot()
    def signal_layer_changed_thickness(self):
        self.undostack.push(
            CDCommandLayerThickness(self, self._active_layer, self.parent().parent().layer_prop_thickness.value()))

    @pyqtSlot()
    def signal_layer_up(self):
        if self._active_layer > 0:
            self.undostack.push(CDCommandLayerUp(self, self._active_layer))

    @pyqtSlot()
    def signal_layer_down(self):
        if self._active_layer < len(self.chip_layers) - 1:
            self.undostack.push(CDCommandLayerDown(self, self._active_layer))

    ###########################################################################
    #                                                                         #
    #  Chip size methods                                                      #
    #                                                                         #
    ###########################################################################

    @pyqtSlot(int)
    def signal_width_changed(self, width):
        self.undostack.push(CDCommandChangeChipWidth(self, width))

    @pyqtSlot(int)
    def signal_height_changed(self, height):
        self.undostack.push(CDCommandChangeChipHeight(self, height))

    @pyqtSlot(int)
    def signal_margins_changed(self, margins):
        self.undostack.push(CDCommandChangeChipMargins(self, margins))

    ###########################################################################
    #                                                                         #
    #  Mouse handling methods                                                 #
    #                                                                         #
    ###########################################################################

    def translate(self, dx: float, dy: float) -> None:
        super().translate(dx, dy)
        self.recalcSnaps()

    def recalcSnaps(self):
        temp_list = []
        for layer in self.chip_layers:
            temp_list += layer.getSnaps()

        self.snaplist.clear()
        for snap in temp_list:
            self.snaplist.append(self.mapFromScene(snap))

    def resizeEvent(self, event) -> None:
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.scale(self.zoom_total, self.zoom_total)

        self.recalcSnaps()

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        # TODO: Somehow the mouse wheel events feel a bit sluggish. Sometimes it goes back, etc.

        if modifiers == Qt.KeyboardModifier.ControlModifier:
            # Set Anchors
            self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
            self.setResizeAnchor(QGraphicsView.ViewportAnchor.NoAnchor)

            # Save the scene pos
            old_pos = self.mapToScene(event.position().toPoint())

            # Zoom
            if event.angleDelta().y() > 0:
                zoom_factor = 1.25
            else:
                zoom_factor = 0.8

            self.scale(zoom_factor, zoom_factor)

            # Get the new position
            new_pos = self.mapToScene(event.position().toPoint())

            self.zoom_total *= zoom_factor

            # Move scene to old position
            delta = new_pos - old_pos
            self.translate(delta.x(), delta.y())

        elif modifiers == Qt.KeyboardModifier.ShiftModifier:
            self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)

            transform = self.transform()
            dx = (50 if event.angleDelta().y() > 0 else -50) / transform.m11()

            self.translate(dx, 0)

        elif modifiers == Qt.KeyboardModifier.NoModifier:
            transform = self.transform()
            dy = (50 if event.angleDelta().y() > 0 else -50) / transform.m22()

            self.translate(0, dy)

        elif modifiers == Qt.KeyboardModifier.AltModifier:
            if self.floating_item:
                # Strangest thing: when Alt is pressed, the mouse wheel 'direction' changes to horizontal
                self.floating_item.rescale(1.1 if event.angleDelta().x() > 0 else 0.9)

    def enterEvent(self, event: QEnterEvent) -> None:
        if self.floating_item:
            self.floating_item.setVisible(True)
            self.floating_item.setPos(self.mapToScene(event.position().toPoint()))

    def leaveEvent(self, event: QEvent) -> None:
        if self.floating_item:
            self.floating_item.setVisible(False)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        # TODO: Implement snapping of a selected item/group
        # TODO: Implement snapping to many other snapping points, for vertical/horizontal alignment, etc
        if self.floating_item:
            # TODO: Implement that the item cannot leave the drawing area
            self.floating_item.setPos(self.mapToScene(event.position().toPoint()))

            flsnaps = self.floating_item.getSnaps()

            coords = self.getSnapCoordinates(flsnaps)
            if coords:
                self.floating_item.snapTo(*coords)
            return
        elif not self.scene().selectedItems() and event.buttons() == Qt.MouseButton.LeftButton and self.selected_items:
            self.selected_items.clear()
            self.selected_items_old_positions.clear()
        elif self.scene().selectedItems() and not self.selected_items:
            for item in self.scene().selectedItems():
                self.selected_items.append(item)
                self.selected_items_old_positions.append(item.pos())
        elif self.selected_items and event.buttons() == Qt.MouseButton.LeftButton:
            print("We need to snap!")
            # First, get all current objects, including their position compared to the mouse
            # Then, set the new position for all objects
            # Get the snapping positions of all objects
            # For each list of positions, ask whether one of their positions is a snapping one
            # For the first hit, make sure everything snaps!

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self.floating_item:
            return
        elif self.scene().selectedItems():
            print("We have selected items")
            # There are selected items. So save the current items and their current positions
            self.selected_items.clear()
            self.selected_items_old_positions.clear()

            for item in self.scene().selectedItems():
                self.selected_items.append(item)
                self.selected_items_old_positions.append(item.pos())

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.floating_item:
            if event.button() == Qt.MouseButton.LeftButton:
                self.undostack.push(CDCommandItemAdd(
                    self, self._active_layer, self.floating_item.copy()
                ))
            elif event.button() == Qt.MouseButton.RightButton:
                self.floating_item.setRotation((self.floating_item.rotation() + 90) % 360)
        elif self.selected_items and event.button() == Qt.MouseButton.LeftButton:
            print("Some items survived the drag event")
            moved = False
            for i, item in enumerate(self.selected_items):
                if item.pos() != self.selected_items_old_positions[i]:
                    moved = True

            if moved:
                movelist = []
                for i, item in enumerate(self.selected_items):
                    movelist.append((item, self.selected_items_old_positions[i], item.pos()))

                self.undostack.push(CDCommandItemsMove(self, movelist))
        else:
            self.selected_items.clear()
            self.selected_items_old_positions.clear()

        super().mouseReleaseEvent(event)

    def getSnapCoordinates(self, points):
        for i, point in enumerate(points):
            real = self.mapFromScene(point)
            for snap in self.snaplist:
                d = math.sqrt((snap.x() - real.x()) ** 2 + (snap.y() - real.y()) ** 2)
                if d < 20:
                    return i, self.mapToScene(snap)

        return None

    def keyPressEvent(self, event: QKeyEvent) -> None:
        match event.key():
            case Qt.Key.Key_Left:
                print("Left key pressed")
            case Qt.Key.Key_Right:
                print("Right key pressed")
            case Qt.Key.Key_Up:
                print("Up key pressed")
            case Qt.Key.Key_Down:
                print("Down key pressed")

    ###########################################################################
    #                                                                         #
    #  Cut/Paste/Copy                                                         #
    #                                                                         #
    ###########################################################################

    @pyqtSlot()
    def signal_cut(self):
        print("Should be cutting")

    @pyqtSlot()
    def signal_copy(self):
        print("Should be copying")

    @pyqtSlot()
    def signal_paste(self):
        print("Should be pasting")

    @pyqtSlot()
    def signal_delete(self):
        pass

    @pyqtSlot()
    def signal_select_all(self):
        pass

    ###########################################################################
    #                                                                         #
    #  Loading and saving                                                     #
    #                                                                         #
    ###########################################################################

    def project_new(self):
        self.layer_model.beginResetModel()
        for layer in self.chip_layers:
            self.scene().removeItem(layer)
        self.chip_layers = []
        self.layer_model.endResetModel()

        # TODO: Change this to adhere to the defaults in the settings file
        self.chip_width = self.parent().parent().spinner_width.value()
        self.chip_height = self.parent().parent().spinner_height.value()
        self.chip_margin = self.parent().parent().spinner_margins.value()
        self.chip_layers = []

        # TODO: Allow user to change the theme
        self.themelist = CDThemeList(os.path.dirname(self.parent().parent().settings.fileName()))
        self.theme = self.themelist.getTheme("Default")

        # Load materials into the material properties list
        for i, material in enumerate(self.theme.materials()):
            self.parent().parent().layer_prop_material.addItem(icon_from_color(material.displayColor), material.name)

        # Install scene, and set some scene properties
        self.setScene(QGraphicsScene(-self.chip_margin,
                                     -self.chip_margin,
                                     self.chip_width + 2 * self.chip_margin,
                                     self.chip_height + 2 * self.chip_margin))

        # Set the background item
        self.background = QGraphicsRectItem(0, 0, 1, 1)
        self.background.setBrush(QBrush(Qt.GlobalColor.white))
        self.background.setPen(QPen(Qt.PenStyle.NoPen))
        self.background.setZValue(-1000)
        self.scene().addItem(self.background)

        # Set the chip outline item
        self.chip_outline = QGraphicsRectItem(0, 0, 1, 1)
        self.chip_outline.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        self.chip_outline.setPen(QPen(QBrush(Qt.GlobalColor.black), 0.01, Qt.PenStyle.DashLine))
        self.chip_outline.setZValue(10)
        self.scene().addItem(self.chip_outline)

        self.setOutlines()

        # Set scene selection properties
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setRubberBandSelectionMode(Qt.ItemSelectionMode.ContainsItemShape)

        # Zooming factor
        self.zoom_total = 1

        # Mouse stuff
        self.floating_item = None
        self.snaplist = []

        self.selected_items = []
        self.selection_moved = False
        self.selected_items_old_positions = []

        self.initEmptyScene()
        self.setActiveLayer(0)

        self.undostack.clear()
