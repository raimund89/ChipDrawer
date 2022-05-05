import ctypes
import pathlib

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from mainwindow import MainWindow

# TODO: Project saving/loading
# TODO: Programmatically load blocks from file
# TODO: Show materials dialog to choose the correct material
# TODO: Load a theme from file including the material properties
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

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("chipdrawer.chipdrawer.v0.1")

    match settings.value("style"):
        case "dark":
            apply_stylesheet(app, theme='dark_amber.xml', extra=extra)
        case "light":
            apply_stylesheet(app, theme='light_cyan.xml', extra=extra)
        case _:
            apply_stylesheet(app, theme='dark_amber.xml', extra=extra)

    window = MainWindow(settings)

    window.show()
    app.exec()
