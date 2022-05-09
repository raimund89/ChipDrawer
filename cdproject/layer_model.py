import typing

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QBrush


class LayerModel(QAbstractTableModel):
    def __init__(self, parent, project):
        super().__init__(parent)

        self._project = project

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._project.chip_layers)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 3

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            match section:
                case 0:
                    return "V"
                case 1:
                    return "M"
                case 2:
                    return "Name"

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        row = index.row()
        column = index.column()

        match role:
            case Qt.ItemDataRole.DisplayRole:
                return self._project.chip_layers[row].name if column == 2 else ""
            case Qt.ItemDataRole.CheckStateRole:
                if column == 0:
                    return Qt.CheckState.Checked if self._project.chip_layers[
                        row].isVisible() else Qt.CheckState.Unchecked
            case Qt.ItemDataRole.BackgroundRole:
                return (QBrush(self._project.chip_layers[row].material.displayColor), QBrush(
                    self._project.chip_layers[row].background_material.displayColor)) if column == 1 else None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
