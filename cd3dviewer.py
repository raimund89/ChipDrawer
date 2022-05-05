import pyvista as pv
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QDialog, QFrame, QVBoxLayout
from pyvistaqt import QtInteractor


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

            if layer.substrate:
                c = pv.Cube((0, 0, z_cur + layer.thickness), self.project.chip_width, self.project.chip_height,
                            layer.thickness * 2)
                self.plotter.add_mesh(c, show_edges=False, **theme.substrate3d)

                z_cur += 2 * layer.thickness

            c = pv.Cube((0, 0, z_cur + layer.thickness / 2), self.project.chip_width, self.project.chip_height,
                        layer.thickness)
            self.plotter.add_mesh(c, show_edges=False, **props)

            z_cur += layer.thickness

        self.plotter.update()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.plotter.close()
