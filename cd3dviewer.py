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
        self.plotter.enable_anti_aliasing()
        self.plotter.enable_eye_dome_lighting()
        # TODO: Enable shadows
        # TODO: Enable eye dome rendering
        # self.plotter.enable_eye_dome_lighting()
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
                self.plotter.add_mesh(c, **theme.substrate3d)

                z_cur += 2 * layer.thickness

            c = pv.Cube((0, 0, z_cur + layer.thickness / 2), self.project.chip_width, self.project.chip_height,
                        layer.thickness)
            self.plotter.add_mesh(c, **bg_props)

            for item in layer.childItems():
                if type(item) is QGraphicsRectItem:
                    continue

                info = item.getData()

                match info['type']:
                    case 'straight':
                        c = pv.Cube((0, 0, z_cur + layer.thickness / 2), item.width, item.length,
                                    layer.thickness)
                        c.rotate_z(item.rotation() - 90, inplace=True)
                        c.translate(self.chiptrans(item.pos().x(), item.pos().y()), inplace=True)
                        self.plotter.add_mesh(c, **props)
                    case 'bend':
                        r = pv.Rectangle([[0, item._radius - item._width / 2, z_cur],
                                          [0, item._radius + item._width / 2, z_cur],
                                          [0, item._radius + item._width / 2, z_cur + layer.thickness],
                                          [0, item._radius - item._width / 2, z_cur + layer.thickness]])
                        curve = r.extrude_rotate(resolution=40, angle=90, capping=True)
                        curve.translate((item._radius / SQRT_2, -item._radius / SQRT_2, 0), inplace=True)
                        curve.rotate_z(-item.rotation(), inplace=True)

                        curve.translate(self.chiptrans(item.pos().x(), item.pos().y()), inplace=True)
                        self.plotter.add_mesh(curve, **props)

            z_cur += layer.thickness

        self.plotter.update()

    def chiptrans(self, x, y):
        return - x + self.project.chip_width / 2, y - self.project.chip_height / 2, 0

    def closeEvent(self, event: QCloseEvent) -> None:
        self.plotter.close()
