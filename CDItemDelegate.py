from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush
from PyQt6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem


class CDItemDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super(CDItemDelegate, self).__init__(parent)

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
        bg = index.data(Qt.ItemDataRole.BackgroundRole)

        if bg and type(bg) is QBrush:
            painter.fillRect(option.rect.adjusted(5, 5, -5, -5), bg)

        super(CDItemDelegate, self).paint(painter, option, index)
