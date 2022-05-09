import ctypes
import os
import pathlib
import time

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QSplashScreen
from qt_material import apply_stylesheet

from buildingblocks import CDBuildingBlockList
from cdproject.theme import CDThemeList
from mainwindow import MainWindow

# TODO: Programmatically load blocks from file
# TODO: Show materials dialog to choose the correct material
# TODO: Scaling and rotating items using handles
# TODO: Rotate a group of items
# TODO: Scale a group of items
# TODO: Reimplement the handles of a line, path, etc to match the stroke
# TODO: Selecting (only for current layer, or for all layers??)
# TODO: Ctrl+C, Ctrl+V, Ctrl+X, Del, Ctrl+A
# TODO: Export/import of other data structures (svg, png, pdf, etc)
# TODO: Saving group of elements as custom block
# TODO: Full support for themes
# TODO: Theme editor
# TODO: 3D viewer
# TODO: Show object properties (width, etc) when selected (requires GUI addition)
# TODO: Snapping gives small gaps between objects.
# TODO: Add tooltip to the building blocks
# TODO: Snap to vertical and horizontal lines that give alignment with other objects
# TODO: Remove _active_layer property, rely completely on the QTableView selected item info
# TODO: Remove the parent().parent() calls that we regularly make right now

extra = {
    # Button colors
    'danger': '#dc3545',
    'warning': '#ffc107',
    'success': '#17a2b8',

    # Font
    'font_family': 'Roboto',
}

if __name__ == "__main__":
    app = QApplication([])
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("chipdrawer.chipdrawer.v0.1")

    splash = QSplashScreen(QPixmap("graphics/splash.png"))
    splash.show()

    splash.showMessage("Loading settings...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                       Qt.GlobalColor.white)

    settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, "Chip Drawer", "Chip Drawer")

    # If the style setting doesn't exist, create it
    if not settings.contains("style"):
        settings.setValue("style", "dark")
    if not settings.contains("default_theme"):
        settings.setValue("default_theme", "Default")
    if not settings.contains("default_directory"):
        settings.setValue("default_directory", str(pathlib.Path.home()))
    if not settings.contains("default_chip_width"):
        settings.setValue("default_chip_width", 20)
    if not settings.contains("default_chip_height"):
        settings.setValue("default_chip_height", 10)
    if not settings.contains("default_chip_margin"):
        settings.setValue("default_chip_margin", 2)

    settings.sync()

    splash.showMessage("Loading themes and blocks...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                       Qt.GlobalColor.white)

    tl = CDThemeList(os.path.dirname(settings.fileName()))
    tl.installThemes()
    bl = CDBuildingBlockList(None, os.path.dirname(settings.fileName()))
    bl.installBlocks()

    splash.showMessage("Setting window styles...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                       Qt.GlobalColor.white)

    match settings.value("style"):
        case "dark":
            apply_stylesheet(app, theme='dark_amber.xml', extra=extra)
        case "light":
            apply_stylesheet(app, theme='light_cyan.xml', extra=extra)
        case _:
            apply_stylesheet(app, theme='dark_amber.xml', extra=extra)

    splash.showMessage("Starting main window...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                       Qt.GlobalColor.white)

    time.sleep(1)

    window = MainWindow(settings)

    window.show()
    app.exec()
