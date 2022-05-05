import glob
import os

from PyQt6.QtCore import QByteArray, QSize, Qt
from PyQt6.QtGui import QImage, QIcon, QPixmap
from PyQt6.QtWidgets import QPushButton, QSpacerItem, QSizePolicy
from yaml import load

from buildingblocks.blocks import CDBlockStraight, CDBlockBend, CDBlockTaper

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


BLOCKITEMS = {
    'mouse': None,
    'straight': CDBlockStraight,
    'bend': CDBlockBend,
    'taper': CDBlockTaper
}


class CDBlockButton(QPushButton):
    def __init__(self, project, icon, block):
        super().__init__(icon, "")

        self.block = block

        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setIconSize(QSize(100, 100))
        self.setStyleSheet("QPushButton {\
                                border: 2px solid black;\
                                min-width: 99px;\
                                min-height: 99px;\
                                max-width: 104px;\
                                max-height: 104px;\
                                padding: 0px;\
                            }\
                            QPushButton:checked {\
                                background-color: #BBB;\
                            }"
                           )

        self.clicked.connect(project.signal_toolbox_clicked)


class CDBuildingBlockList:
    def __init__(self, mainwindow, directory):
        # Loading the list of themes from the disk
        self.directory = directory + "/blocks"
        self.project = mainwindow.drawing_area
        self.box_standard = mainwindow.standard_blocks_layout.layout()
        self.box_custom = mainwindow.custom_blocks_layout.layout()

        self._blocks = {
            'standard': [],
            'custom': []
        }

        if not os.path.isdir(self.directory):
            self.installBlocks()

        self.loadBlocks()

    def installBlocks(self):
        os.mkdir(self.directory)
        os.mkdir(self.directory + "/standard")
        os.mkdir(self.directory + "/custom")
        # TODO: Download standard blocks from github. If it doesn't work, show a big error

    def loadBlocks(self):
        for block in glob.glob(self.directory + "/standard/*.yaml"):
            with open(block, "r") as f:
                data = load(f, Loader=Loader)
                self.parseBlock('standard', data)
        for block in glob.glob(self.directory + "/custom/*.yaml"):
            with open(block, "r") as f:
                data = load(f, Loader=Loader)
                self.parseBlock('custom', data)

        i, j = 0, 0
        for block in self._blocks['standard']:
            self.box_standard.addWidget(
                CDBlockButton(self.project, block['image'], block['block']),
                i,
                j,
                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
            )

            if j < 2:
                j += 1
            else:
                j = 0
                i += 1

        self.box_standard.addItem(QSpacerItem(20, 40, vPolicy=QSizePolicy.Policy.Expanding), i+1, 0, rowSpan=1, columnSpan=3)

        i, j = 0, 0
        for block in self._blocks['custom']:
            self.box_custom.addWidget(
                CDBlockButton(self.project, block['image'], block['block']),
                i,
                j,
                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
            )

            if j < 2:
                j += 1
            else:
                j = 0
                i += 1

    def parseBlock(self, library, data):
        self._blocks[library].append({
            'name': data['name'],
            'description': data['description'],
            'block': BLOCKITEMS[data['type']],
            'image': QIcon(
                QPixmap.fromImage(QImage.fromData(QByteArray.fromBase64(data['image'].encode('utf-8')), "PNG")))
        })
