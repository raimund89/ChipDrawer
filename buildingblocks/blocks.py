from PyQt6.QtCore import QPoint, QPointF, QRectF, Qt
from PyQt6.QtGui import QPainterPath
from PyQt6.QtWidgets import QApplication

from buildingblocks.blockitem import CDBlockItem, DEFAULT_WIDTH, SQRT_2, array2transform, transform2array


# TODO: Make pen size and handle size dependent on pixels, not on the scene coordinates
# TODO: On select, set the Z-value for the selected block higher
# TODO: Don't show selection per item, but for the entire group of items


class CDBlockStraight(CDBlockItem):
    DEFAULT_LENGTH = 2.0

    def __init__(self, w=None, l=None):
        super().__init__()

        self._width = DEFAULT_WIDTH if not w else w
        self._length = self.DEFAULT_LENGTH if not l else l

        self.snaps = []

        self.handles = []
        self.handleSelected = None

        self.createPath()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, w):
        self._width = w
        self.createPath()

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, l):
        self._length = l
        self.createPath()

    def rescale(self, scale: float) -> None:
        self._length = self._length * scale
        self.createPath()

    def createPath(self):
        self.snaps = [QPointF(-self._length / 2, 0), QPointF(self._length / 2, 0)]

        p = QPainterPath()
        p.addRect(-self._length / 2, -self._width / 2, self._length, self._width)

        self.setPath(p)

        # Now also update the handles
        try:
            dpi = QApplication.instance().activeWindow().screen().physicalDotsPerInch()
            # lasjdfljkasdl
            # TODO: Implement this in the right way!
            hsize = QApplication.instance().activeWindow().drawing_area.mapToScene(
                QPoint(int(dpi * 0.01 / 25.4), 0)).x()  # 25.4 mm/inch
        except AttributeError:
            hsize = 0.02

        self.handles = [
            (Qt.CursorShape.SizeHorCursor if self.rotation() % 180 == 0 else Qt.CursorShape.SizeVerCursor,
             QRectF(-self._length / 2 - hsize / 2, -hsize / 2, hsize, hsize)),
            (Qt.CursorShape.SizeHorCursor if self.rotation() % 180 == 0 else Qt.CursorShape.SizeVerCursor,
             QRectF(self._length / 2 - hsize / 2, -hsize / 2, hsize, hsize))
        ]

    def copy(self):
        b = CDBlockStraight(self._width, self._length)
        b.setBrush(self.brush())
        b.setPos(self.pos())
        b.setTransform(self.transform())
        b.setFlags(self.flags())
        return b

    # # TODO: Stuff to implement to allow resizing
    # def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem',
    #           widget: typing.Optional[QWidget] = ...) -> None:
    #     super().paint(painter, option, widget)
    #
    #     if self.isSelected():
    #         painter.setBrush(QBrush(Qt.GlobalColor.green))
    #         painter.setPen(QPen(Qt.PenStyle.NoPen))
    #
    #         for handle, rect in self.handles:
    #             if self.handleSelected is None or handle == self.handleSelected:
    #                 painter.drawRect(rect)

    #
    # def boundingRect(self) -> QRectF:
    #     return super().boundingRect().adjusted(-0.04, -0.04, 0.04, 0.04)
    #
    # def handleAt(self, point):
    #     for k, v in self.handles:
    #         if v.contains(point):
    #             return k
    #     return None
    #
    # def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
    #     print("Everything is hovering!")
    #     if self.isSelected():
    #         print("I'm selected, and hovered")
    #         handle = self.handleAt(event.pos())
    #         cursor = Qt.CursorShape.ArrowCursor if handle is None else handle
    #         self.setCursor(cursor)
    #
    #     super().hoverMoveEvent(event)
    #
    # def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
    #     self.setCursor(Qt.CursorShape.ArrowCursor)
    #     super().hoverLeaveEvent(event)
    #
    # def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
    #     self.handleSelected = self.handleAt(event.pos())
    #     if self.handleSelected:
    #         self.mousePressPos = event.pos()
    #         self.mousePressRect = self.boundingRect()
    #     super().mousePressEvent(event)
    #
    # def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
    #     if self.handleSelected is not None:
    #         self.interactiveResize(event.pos())
    #     else:
    #         super().mouseMoveEvent(event)
    #
    # def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
    #     super().mouseReleaseEvent(event)
    #     self.handleSelected = None
    #     self.mousePressPos = None
    #     self.mousePressRect = None
    #     self.update()
    #
    # def interactiveResize(self, mousePos):
    #     offset = 0.04
    #     boundingRect = self.boundingRect()
    #     rect = super().boundingRect()
    #     diff = QPointF(0, 0)
    #
    #     self.prepareGeometryChange()
    #
    #     self.createPath()

    # TODO: Support to name the data blocks
    def getData(self):
        return {
            'name': 'Straight',
            'type': 'straight',
            'width': self._width,
            'length': self._length,
            'position': {
                'x': self.pos().x(),
                'y': self.pos().y()
            },
            'transformation': transform2array(self.transform())
        }

    def loadData(self, data):
        # TODO: Implement name
        self.width = data['width']
        self.length = data['length']
        self.setPos(QPointF(data['position']['x'], data['position']['y']))
        self.setTransform(array2transform(data['transformation']))


class CDBlockBend(CDBlockItem):
    DEFAULT_RADIUS = 3.0

    def __init__(self, w=None, r=None):
        super().__init__()

        self._width = DEFAULT_WIDTH if not w else w
        self._radius = self.DEFAULT_RADIUS if not r else r

        self.snaps = []

        self.createPath()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, w):
        self._width = w
        self.createPath()

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, r):
        self._radius = r
        self.createPath()

    def rescale(self, scale: float) -> None:
        self._radius = self._radius * scale
        self.createPath()

    def createPath(self):
        center = QPointF(-self._radius / SQRT_2, -self._radius / SQRT_2)

        p = QPainterPath()
        p.moveTo(center.x() + (self._radius - self._width / 2), center.y())
        p.arcTo(center.x() - (self._radius - self._width / 2), center.y() - (self._radius - self._width / 2),
                2 * (self._radius - self._width / 2), 2 * (self._radius - self._width / 2), 0, -90)
        p.lineTo(center.x(), center.y() + self._radius + self._width / 2)
        p.arcTo(center.x() - (self._radius + self._width / 2), center.y() - (self._radius + self._width / 2),
                2 * (self._radius + self._width / 2), 2 * (self._radius + self._width / 2), -90, 90)
        p.lineTo(center.x() + (self._radius - self._width / 2), center.y())

        self.snaps = [QPointF(center.x() + self._radius, center.y()),
                      QPointF(center.x(), center.y() + self._radius)]

        self.setPath(p)

    def copy(self):
        b = CDBlockBend(self._width, self._radius)
        b.setBrush(self.brush())
        b.setPos(self.pos())
        b.setTransform(self.transform())
        b.setFlags(self.flags())
        return b

    # TODO: Support to name the data blocks
    def getData(self):
        return {
            'name': 'Bend',
            'type': 'bend',
            'width': self._width,
            'radius': self._radius,
            'position': {
                'x': self.pos().x(),
                'y': self.pos().y()
            },
            'transformation': transform2array(self.transform())
        }

    def loadData(self, data):
        # TODO: Implement name
        self.width = data['width']
        self.radius = data['radius']
        self.setPos(QPointF(data['position']['x'], data['position']['y']))
        self.setTransform(array2transform(data['transformation']))


class CDBlockTaper(CDBlockItem):
    DEFAULT_LENGTH = 2.0

    def __init__(self, w1=None, w2=None, l=None):
        super().__init__()

        self._width = DEFAULT_WIDTH if not w1 else w1
        self._width2 = 2 * DEFAULT_WIDTH if not w2 else w2
        self._length = self.DEFAULT_LENGTH if not l else l

        self.snaps = []

        self.createPath()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, w1):
        self._width = w1
        self.createPath()

    @property
    def width2(self):
        return self._width2

    @width2.setter
    def width2(self, w2):
        self._width2 = w2
        self.createPath()

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, l):
        self._length = l
        self.createPath()

    def rescale(self, scale: float) -> None:
        self._length = self._length * scale
        self.createPath()

    def createPath(self):
        self.snaps = [QPointF(-self._length / 2, 0), QPointF(self._length / 2, 0)]

        p = QPainterPath()
        p.moveTo(-self._length / 2, -self._width / 2)
        p.lineTo(self._length / 2, -self._width2 / 2)
        p.lineTo(self._length / 2, self._width2 / 2)
        p.lineTo(-self._length / 2, self._width / 2)
        p.lineTo(-self._length / 2, -self._width / 2)

        self.setPath(p)

    def copy(self):
        b = CDBlockTaper(self._width, self._width2, self._length)
        b.setBrush(self.brush())
        b.setPos(self.pos())
        b.setTransform(self.transform())
        b.setFlags(self.flags())
        return b

    # TODO: Support to name the data blocks
    def getData(self):
        return {
            'name': 'Taper',
            'type': 'taper',
            'width': self._width,
            'width2': self._width2,
            'length': self._length,
            'position': {
                'x': self.pos().x(),
                'y': self.pos().y()
            },
            'transformation': transform2array(self.transform())
        }

    def loadData(self, data):
        # TODO: Implement name
        self.width = data['width']
        self.width2 = data['width2']
        self.length = data['length']
        self.setPos(QPointF(data['position']['x'], data['position']['y']))
        self.setTransform(array2transform(data['transformation']))


class CDBlockSBend(CDBlockItem):
    DEFAULT_LENGTH = 2.0
    DEFAULT_SIDE = 1.0

    def __init__(self, w=None, l=None, s=None):
        super().__init__()

        self._width = DEFAULT_WIDTH if not w else w
        self._side = self.DEFAULT_SIDE if not s else s
        self._length = self.DEFAULT_LENGTH if not l else l

        self.snaps = []

        self.createPath()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, w):
        self._width = w
        self.createPath()

    @property
    def side(self):
        return self._side

    @side.setter
    def side(self, s):
        self._side = s
        self.createPath()

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, l):
        self._length = l
        self.createPath()

    def rescale(self, scale: float) -> None:
        self._length = self._length * scale
        self.createPath()

    def createPath(self):
        self.snaps = [QPointF(-self._length / 2, -self._side / 2), QPointF(self._length / 2, self._side / 2)]

        p = QPainterPath()
        # TODO: Find a better method than the /3 for the control points
        p.moveTo(-self._length / 2, -self._side / 2 - self._width / 2)
        p.cubicTo(QPointF(self._width / 3, -self._side / 2 - self._width / 2),
                  QPointF(self._width / 3, self._side / 2 - self._width / 2),
                  QPointF(self._length / 2, self._side / 2 - self._width / 2))
        p.lineTo(QPointF(self._length / 2, self._side / 2 + self._width / 2))
        p.cubicTo(QPointF(-self._width / 3, self._side / 2 + self._width / 2),
                  QPointF(-self._width / 3, -self._side / 2 + self._width / 2),
                  QPointF(-self._length / 2, -self._side / 2 + self._width / 2))
        p.lineTo(QPointF(-self._length / 2, -self._side / 2 - self._width / 2))

        self.setPath(p)

    def copy(self):
        b = CDBlockSBend(self._width, self._length, self._side)
        b.setBrush(self.brush())
        b.setPos(self.pos())
        b.setTransform(self.transform())
        b.setFlags(self.flags())
        return b

    # TODO: Support to name the data blocks
    def getData(self):
        return {
            'name': 'S-Bend',
            'type': 's-bend',
            'width': self._width,
            'side': self._side,
            'length': self._length,
            'position': {
                'x': self.pos().x(),
                'y': self.pos().y()
            },
            'transformation': transform2array(self.transform())
        }

    def loadData(self, data):
        # TODO: Implement name
        self.width = data['width']
        self.side = data['side']
        self.length = data['length']
        self.setPos(QPointF(data['position']['x'], data['position']['y']))
        self.setTransform(array2transform(data['transformation']))
