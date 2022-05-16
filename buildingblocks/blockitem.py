import math
import typing

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QPainter, QPainterPath, QPen, QTransform
from PyQt6.QtWidgets import QGraphicsPathItem, QStyleOptionGraphicsItem, QWidget

SNAP_MAX = 1e6

DEFAULT_WIDTH = 0.2
SQRT_2 = math.sqrt(2)


class CDBlockItem(QGraphicsPathItem):
    def __init__(self):
        super().__init__()
        self.setAcceptHoverEvents(True)

        self.setBrush(QBrush(Qt.GlobalColor.red))
        self.setPen(QPen(Qt.PenStyle.NoPen))

        self._snaps = []

    def setRotation(self, angle: float) -> None:
        self.setTransform(self.transform().rotate(angle))

    def setScale(self, scale: float) -> None:
        self.setTransform(self.transform().scale(scale, scale))

    @property
    def snaps(self):
        return self._snaps

    @snaps.setter
    def snaps(self, s):
        self._snaps = s

    def getSnaps(self):
        return [self.mapToScene(p) for p in self._snaps]

    def snapTo(self, index, t, point):
        self.setPos(point - self.transform().map(self._snaps[index]))

    def shape(self) -> QPainterPath:
        return self.path()

    def createPath(self):
        raise NotImplementedError

    def getData(self):
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

    def flip(self, horizontal=True):
        t = self.transform()
        if horizontal:
            self.setTransform(t.scale(-1, 1))
        else:
            self.setTransform(t.scale(1, -1))


def transform2array(t: QTransform):
    return [t.m11(), t.m12(), t.m13(), t.m21(), t.m22(), t.m23(), t.m31(), t.m32(), t.m33()]


def array2transform(a):
    return QTransform(*a)
