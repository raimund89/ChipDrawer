import pyvista as pv
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QDialog, QFrame, QGraphicsRectItem, QVBoxLayout
from pyvistaqt import QtInteractor

from buildingblocks.blockitem import SQRT_2


class CD3DViewer(QDialog):
    def __init__(self, parent=None, project=None):
        super().__init__(parent)

        self.setModal(False)
        self.setMinimumSize(800, 600)

        self.project = project

        self.frame = QFrame()
        vlayout = QVBoxLayout()
        vlayout.addWidget(self.frame)
        self.setLayout(vlayout)

        # add the pyvista interactor object
        self.plotter = QtInteractor(self.frame)
        vlayout.addWidget(self.plotter.interactor)

        self.show()

        self.updateChip()
        self.plotter.reset_camera()

    def updateChip(self):
        self.plotter.background_color = 'white'
        self.plotter.clear()

        z_cur = 0

        theme = self.project.theme

        for layer in reversed(self.project.chip_layers):
            props = layer.material.get3D()
            bg_props = layer.background_material.get3D()

            if layer.substrate:
                c = pv.Cube((0, 0, z_cur + layer.thickness), self.project.chip_width, self.project.chip_height,
                            layer.thickness * 2)
                self.plotter.add_mesh(c, show_edges=False, **theme.substrate3d)

                z_cur += 2 * layer.thickness

            c = pv.Cube((0, 0, z_cur + layer.thickness / 2), self.project.chip_width, self.project.chip_height,
                        layer.thickness)
            self.plotter.add_mesh(c, show_edges=False, **bg_props)

            for item in layer.childItems():
                if type(item) is QGraphicsRectItem:
                    continue

                info = item.getData()

                match info['type']:
                    case 'straight':
                        c = pv.Cube((0, 0, z_cur + layer.thickness / 2), item.width, item.length,
                                    layer.thickness)
                        c.rotate_z(item.rotation() - 90)
                        c.translate(self.chiptrans(item.pos().x(), item.pos().y()))
                        self.plotter.add_mesh(c, show_edges=False, **props)
                    case 'bend':
                        center = [-item._radius / SQRT_2, -item._radius / SQRT_2]

                        arc2 = pv.CircularArc([center[0] + item._radius + item._width / 2, center[1], z_cur],
                                              [center[0], center[1] + item._radius + item._width / 2, z_cur],
                                              [center[0], center[1], z_cur])

                        poly = arc2.extrude([0, 0, layer.thickness], capping=False)
                        # poly = poly.extrude([item._width, item._width, 0], capping=False)
                        # poly.rotate_z(-item.rotation() + 90)
                        # poly.translate(self.chiptrans(item.pos().x(), item.pos().y()))
                        self.plotter.add_mesh(poly, show_edges=False, **props)

            z_cur += layer.thickness

        self.plotter.update()

    def chiptrans(self, x, y):
        return - x + self.project.chip_width / 2, y - self.project.chip_height / 2, 0

    def closeEvent(self, event: QCloseEvent) -> None:
        self.plotter.close()
