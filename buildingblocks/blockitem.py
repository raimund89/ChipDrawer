import math
import typing

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QPainter, QPainterPath, QPen, QTransform
from PyQt6.QtWidgets import QGraphicsPathItem, QStyleOptionGraphicsItem, QWidget

DEFAULT_WIDTH = 0.2
SQRT_2 = math.sqrt(2)


class CDBlockItem(QGraphicsPathItem):
    def __init__(self):
        super().__init__()
        self.setAcceptHoverEvents(True)

        self.setBrush(QBrush(Qt.GlobalColor.red))
        self.setPen(QPen(Qt.PenStyle.NoPen))

        self._snaps = []

    @property
    def snaps(self):
        return self._snaps

    @snaps.setter
    def snaps(self, s):
        self._snaps = s

    def getSnaps(self):
        return [self.mapToScene(s) for s in self._snaps]

    def snapTo(self, index, point):
        transform = QTransform().scale(self.scale(), self.scale()).rotate(self.rotation())
        p = transform.map(self._snaps[index])
        self.setPos(point - p)

    def shape(self) -> QPainterPath:
        return self.path()

    def createPath(self):
        raise NotImplementedError

    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional[QWidget] = ...) -> None:
        painter.setBrush(self.brush())
        painter.setPen(self.pen())
        painter.drawPath(self.path())

        if self.isSelected():
            painter.setBrush((QBrush(Qt.BrushStyle.NoBrush)))
            painter.setPen(QPen(Qt.GlobalColor.black, 0.04, Qt.PenStyle.DashLine))
            painter.drawPath(self.path())

            # TODO: Paint handles for resizing etc.
