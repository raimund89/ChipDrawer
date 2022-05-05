from PyQt6.QtGui import QUndoCommand
from PyQt6.QtWidgets import QGraphicsItem

from cdproject.layer import CDLayer


class CDCommandAddLayer(QUndoCommand):
    def __init__(self, project, position, name, visible, substrate, material):
        super().__init__(f"Add layer {name}")

        self.project = project
        print(self.project.scene)

        self.position = position
        self.name = name
        self.visible = visible
        self.substrate = substrate
        self.material = material

    def redo(self) -> None:
        self.project.layer_model.beginResetModel()

        layer = CDLayer(self.project, self.name)
        layer.setVisible(self.visible)
        layer.substrate = self.substrate
        layer.material = self.material

        self.project.chip_layers.insert(self.position, layer)
        self.project.scene.addItem(self.project.chip_layers[self.position])

        for i, layer in enumerate(self.project.chip_layers):
            layer.setZValue(-i)

        self.project.layer_model.endResetModel()
        self.project.setActiveLayer(self.position)

    def undo(self) -> None:
        self.project.layer_model.beginResetModel()

        self.project.scene.removeItem(self.project.chip_layers[self.position])
        self.project.chip_layers.pop(self.position)

        for i, layer in enumerate(self.project.chip_layers):
            layer.setZValue(-i)

        self.project.layer_model.endResetModel()
        self.project.setActiveLayer(self.position - 1)


class CDCommandRemoveLayer(QUndoCommand):
    def __init__(self, project, position):
        super().__init__(f"Remove layer {project.chip_layers[position].name}")

        self.project = project
        self.position = position

        self.layer = None

    def redo(self) -> None:
        self.project.layer_model.beginResetModel()

        self.layer = self.project.chip_layers[self.position]

        self.project.scene.removeItem(self.project.chip_layers[self.position])
        self.project.chip_layers.pop(self.position)

        for i, layer in enumerate(self.project.chip_layers):
            layer.setZValue(-i)

        self.project.layer_model.endResetModel()
        self.project.setActiveLayer(self.position - 1)

    def undo(self) -> None:
        self.project.layer_model.beginResetModel()

        self.project.chip_layers.insert(self.position, self.layer)
        self.project.scene.addItem(self.project.chip_layers[self.position])

        for i, layer in enumerate(self.project.chip_layers):
            layer.setZValue(-i)

        self.project.layer_model.endResetModel()
        self.project.setActiveLayer(self.position)


class CDCommandChangeChipWidth(QUndoCommand):
    def __init__(self, project, width):
        super().__init__("Change chip width")

        self.project = project
        self.width = width

        self.old_width = self.project.chip_width

    def redo(self) -> None:
        self.project.chip_width = self.width
        self.project.setOutlines()

    def undo(self) -> None:
        self.project.chip_width = self.old_width
        self.project.setOutlines()

        self.project.parent().parent().spinner_width.setValue(self.project.chip_width)


class CDCommandChangeChipHeight(QUndoCommand):
    def __init__(self, project, height):
        super().__init__("Change chip height")

        self.project = project
        self.height = height

        self.old_height = self.project.chip_height

    def redo(self) -> None:
        self.project.chip_height = self.height
        self.project.setOutlines()

    def undo(self) -> None:
        self.project.chip_height = self.old_height
        self.project.setOutlines()

        self.project.parent().parent().spinner_height.setValue(self.project.chip_height)


class CDCommandChangeChipMargins(QUndoCommand):
    def __init__(self, project, margin):
        super().__init__("Change chip margin")

        self.project = project
        self.margin = margin

        self.old_margin = self.project.chip_margin

    def redo(self) -> None:
        self.project.chip_margin = self.margin
        self.project.setOutlines()

    def undo(self) -> None:
        self.project.chip_margin = self.old_margin
        self.project.setOutlines()

        self.project.parent().parent().spinner_margins.setValue(self.project.chip_margin)


class CDCommandLayerMaterial(QUndoCommand):
    def __init__(self, project, position, material):
        super().__init__(f"Change material to {material.name}")

        self.project = project
        self.position = position
        self.material = material

        self.old_material = self.project.chip_layers[self.position].material

    def redo(self) -> None:
        self.project.layer_model.beginResetModel()
        self.project.chip_layers[self.position].material = self.material
        self.project.layer_model.endResetModel()
        self.project.setActiveLayer(self.position)

    def undo(self) -> None:
        self.project.layer_model.beginResetModel()
        self.project.chip_layers[self.position].material = self.old_material
        self.project.layer_model.endResetModel()
        self.project.setActiveLayer(self.position)


class CDCommandLayerName(QUndoCommand):
    def __init__(self, project, position, name):
        super().__init__(f"Change layer name to {name}")

        self.project = project
        self.position = position
        self.name = name

        self.old_name = self.project.chip_layers[self.position].name

    def redo(self) -> None:
        self.project.layer_model.beginResetModel()
        self.project.chip_layers[self.position].name = self.name
        self.project.layer_model.endResetModel()
        self.project.setActiveLayer(self.position)

    def undo(self) -> None:
        self.project.layer_model.beginResetModel()
        self.project.chip_layers[self.position].name = self.old_name
        self.project.layer_model.endResetModel()
        self.project.setActiveLayer(self.position)


class CDCommandLayerVisibility(QUndoCommand):
    def __init__(self, project, position, visible):
        super().__init__(f"Change layer visibility")

        self.project = project
        self.position = position
        self.visible = visible

        self.old_visible = self.project.chip_layers[self.position].isVisible()

    def redo(self) -> None:
        self.project.layer_model.beginResetModel()
        self.project.chip_layers[self.position].setVisible(self.visible)
        self.project.layer_model.endResetModel()
        self.project.setActiveLayer(self.position)

    def undo(self) -> None:
        self.project.layer_model.beginResetModel()
        self.project.chip_layers[self.position].setVisible(self.old_visible)
        self.project.layer_model.endResetModel()
        self.project.setActiveLayer(self.position)


class CDCommandLayerSubstrate(QUndoCommand):
    def __init__(self, project, position, substrate):
        super().__init__(f"Change layer substrate")

        self.project = project
        self.position = position
        self.substrate = substrate

        self.old_substrate = self.project.chip_layers[self.position].substrate

    def redo(self) -> None:
        self.project.layer_model.beginResetModel()
        self.project.chip_layers[self.position].substrate = self.substrate
        self.project.layer_model.endResetModel()
        self.project.setActiveLayer(self.position)

    def undo(self) -> None:
        self.project.layer_model.beginResetModel()
        self.project.chip_layers[self.position].substrate = self.old_substrate
        self.project.layer_model.endResetModel()
        self.project.setActiveLayer(self.position)


class CDCommandLayerThickness(QUndoCommand):
    def __init__(self, project, position, thickness):
        super().__init__(f"Change layer thickness")

        self.project = project
        self.position = position
        self.thickness = thickness

        self.old_thickness = self.project.chip_layers[self.position].thickness

    def redo(self) -> None:
        self.project.layer_model.beginResetModel()
        self.project.chip_layers[self.position].thickness = self.thickness
        self.project.layer_model.endResetModel()
        self.project.setActiveLayer(self.position)

    def undo(self) -> None:
        self.project.layer_model.beginResetModel()
        self.project.chip_layers[self.position].thickness = self.old_thickness
        self.project.layer_model.endResetModel()
        self.project.setActiveLayer(self.position)


class CDCommandLayerUp(QUndoCommand):
    def __init__(self, project, position):
        super().__init__(f"Move layer up")

        self.project = project
        self.position = position

    def redo(self) -> None:
        self.project.layer_model.beginResetModel()
        self.project.chip_layers.insert(self.position - 1, self.project.chip_layers.pop(self.position))

        for i, layer in enumerate(self.project.chip_layers):
            layer.setZValue(-i)

        self.project.layer_model.endResetModel()
        self.project.setActiveLayer(self.position - 1)

    def undo(self) -> None:
        self.project.layer_model.beginResetModel()
        self.project.chip_layers.insert(self.position, self.project.chip_layers.pop(self.position - 1))

        for i, layer in enumerate(self.project.chip_layers):
            layer.setZValue(-i)

        self.project.layer_model.endResetModel()
        self.project.setActiveLayer(self.position)


class CDCommandLayerDown(QUndoCommand):
    def __init__(self, project, position):
        super().__init__(f"Move layer down")

        self.project = project
        self.position = position

    def redo(self) -> None:
        self.project.layer_model.beginResetModel()
        self.project.chip_layers.insert(self.position + 1, self.project.chip_layers.pop(self.position))

        for i, layer in enumerate(self.project.chip_layers):
            layer.setZValue(-i)

        self.project.layer_model.endResetModel()
        self.project.setActiveLayer(self.position + 1)

    def undo(self) -> None:
        self.project.layer_model.beginResetModel()
        self.project.chip_layers.insert(self.position, self.project.chip_layers.pop(self.position + 1))

        for i, layer in enumerate(self.project.chip_layers):
            layer.setZValue(-i)

        self.project.layer_model.endResetModel()
        self.project.setActiveLayer(self.position)


class CDCommandItemAdd(QUndoCommand):
    def __init__(self, project, ilayer, item):
        super().__init__(f"Add item")

        print(project, ilayer, item)

        self.project = project
        self.layer = ilayer
        self.item = item
        self.item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)

    def redo(self) -> None:
        self.item.setParentItem(self.project.chip_layers[self.layer])
        self.project.scene.addItem(self.item)
        self.project.recalcSnaps()

    def undo(self) -> None:
        self.project.scene.removeItem(self.item)
        self.project.recalcSnaps()


class CDCommandItemsMove(QUndoCommand):
    def __init__(self, project, movelist):
        super().__init__("Move items")

        self.project = project
        self.movelist = movelist

    def redo(self) -> None:
        for item in self.movelist:
            item[0].setPos(item[2])
        self.project.recalcSnaps()

    def undo(self) -> None:
        for item in self.movelist:
            item[0].setPos(item[1])
        self.project.recalcSnaps()
