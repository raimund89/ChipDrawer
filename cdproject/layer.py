import typing

from PyQt6 import QtGui
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QPen
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QStyleOptionGraphicsItem, QWidget

from buildingblocks import BLOCKITEMS

DEFAULT_THICKNESS = 0.5


class CDLayer(QGraphicsItem):
    def __init__(self, project, name):
        super().__init__()

        self._project = project
        self._name = name
        self._substrate = None
        self._material = project.theme.material(0)
        self._background_material = project.theme.material(0)
        self._thickness = DEFAULT_THICKNESS

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    @property
    def substrate(self):
        return self._substrate is not None

    @substrate.setter
    def substrate(self, s):
        if s:
            self._substrate = QGraphicsRectItem(0, 0, self._project.chip_width, self._project.chip_height, self)
            self._substrate.setBrush(QBrush(Qt.GlobalColor.blue))
            self._substrate.setPen(QPen(Qt.PenStyle.NoPen))
            self._substrate.setZValue(-20)
            self._project.scene().addItem(self._substrate)
        else:
            if self._substrate:
                self._project.scene().removeItem(self._substrate)
                self._substrate = None

    @property
    def material(self):
        return self._material

    @material.setter
    def material(self, m):
        self._material = m
        for item in self.childItems():
            if item != self._substrate:
                item.setBrush(self._material.getBrush())

    @property
    def background_material(self):
        return self._background_material

    @background_material.setter
    def background_material(self, b):
        self._background_material = b

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, t):
        if t > 0:
            self._thickness = t

    def resize_chip(self):
        if self._substrate:
            self._substrate.setRect(0, 0, self._project.chip_width, self._project.chip_height)

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional[QWidget] = ...) -> None:
        pass

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, 0, 0)

    def getSnaps(self, excludes=None):
        snaps = []
        for item in self.childItems():
            if item != self._substrate and item not in excludes:
                snaps += item.getSnaps()
        return snaps

    def itemChange(self, change: 'QGraphicsItem.GraphicsItemChange', value: typing.Any) -> typing.Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemChildAddedChange:
            if type(value) != QGraphicsItem:
                value.setBrush(self._material.getBrush())

        return super().itemChange(change, value)

    def getData(self):
        return {
            'name': self.name,
            'substrate': self.substrate,
            'visible': self.isVisible(),
            'thickness': self.thickness,
            'material': self.material.name,
            'background_material': self.background_material.name,
            'items': [item.getData() for item in self.childItems() if item != self._substrate]
        }

    def loadData(self, data):
        self.name = data['name']
        self.substrate = data['substrate']
        self.setVisible(data['visible'])
        self.thickness = data['thickness']
        self.material = self._project.theme.material(data['material'])[1]
        self.background_material = self._project.theme.material(data['background_material'])[1]

        for item in data['items']:
            itm = BLOCKITEMS[item['type']]()
            itm.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
            itm.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
            itm.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
            itm.setParentItem(self)
            itm.loadData(item)
            self._project.scene().addItem(itm)
