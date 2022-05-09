from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QStyleOptionViewItem, QStyledItemDelegate


class CDItemDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super(CDItemDelegate, self).__init__(parent)

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
        bg = index.data(Qt.ItemDataRole.BackgroundRole)

        if bg and type(bg) is tuple:
            r = option.rect
            painter.fillRect(option.rect.adjusted(5, 5, int(-r.x() / 2), -5), bg[0])
            painter.fillRect(option.rect.adjusted(int(r.x() / 2), 5, -5, -5), bg[1])

        super(CDItemDelegate, self).paint(painter, option, index)
