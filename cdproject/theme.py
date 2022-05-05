import glob
import os

from PyQt6.QtGui import QColor
from yaml import load

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from cdproject.material import CDMaterial


class CDThemeList:
    def __init__(self, directory):
        # Loading the list of themes from the disk
        self.directory = directory + "/themes"

        self._themes = []

        if not os.path.isdir(self.directory):
            self.installThemes()

        self.loadThemes()

    def installThemes(self):
        os.mkdir(self.directory)
        # TODO: Implement this. Download the themes from github and save in self.directory
        # If no internet connection, display a big fat error

    def loadThemes(self):
        for theme in glob.glob(self.directory + "/*.yaml"):
            self._themes.append(CDTheme(theme))

    def getTheme(self, name):
        for theme in self._themes:
            if theme.name == name:
                return theme

        return None


class CDTheme:
    def __init__(self, filename):
        if not filename:
            # No filename given, so currently we cannot load this theme
            raise ValueError("Theme cannot be loaded due to a missing filename")

        with open(filename, "r") as f:
            data = load(f.read(), Loader=Loader)

        self._name = data['name']

        self._substrate3d = data['substrate']

        self.material_list = []
        for material in data['materials']:
            self.material_list.append(
                CDMaterial(material['name'], QColor(material['color']), material['description'], material['3d']))

    @property
    def name(self):
        return self._name

    def materials(self):
        return self.material_list

    def material(self, i):
        if type(i) is int:
            return self.material_list[i]
        elif type(i) is str:
            for n, material in enumerate(self.material_list):
                if material.name == i:
                    return n, material
            return None

    @property
    def substrate3d(self):
        return self._substrate3d
