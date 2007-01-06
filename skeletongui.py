"""
skeletongui: multi-purpose "blank" dialog
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import mlibgui
import playlistgui
import equalizergui

class SkeletonDialog(QDialog):
    """
    The SkeletonDialog class provides our base GUI which acts as a container
    for the other Sonus GUIs.
    """
    def __init__(self, sonus, parent=None):
        QDialog.__init__(self, parent)

        self.logger = logging.getLogger('Sonus.skeletongui')
        self.sonus = sonus

        self.setWindowTitle(self.tr('Sonus - Manager'))
        self.resize(QSize(640, 360))

        self.gridLayout = QGridLayout(self)

        self.tabWidget = QTabWidget(self)
        self.mlibDialog = mlibgui.MlibDialog(self.sonus)
        self.playlistDialog = playlistgui.PlaylistDialog(self.sonus)
        self.equalizerDialog = equalizergui.EqualizerDialog(self.sonus)
        self.tabWidget.addTab(self.mlibDialog, self.tr('Media &Library'))
        self.tabWidget.addTab(self.playlistDialog, self.tr('&Playlist'))
        self.tabWidget.addTab(self.equalizerDialog, self.tr('&Equalizer'))
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.tabWidget.setCurrentIndex(0)
