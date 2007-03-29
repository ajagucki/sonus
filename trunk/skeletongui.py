"""
Multi-purpose "blank" dialog.
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import mlibgui
import playlistgui
import collectionsgui
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

        self.tabWidget  = QTabWidget(self)

        self.mlibWidget = mlibgui.MlibWidget(self.sonus)
        self.playlistWidget  = playlistgui.PlaylistWidget(self.sonus)
        self.collectionsWidget = collectionsgui.CollectionsWidget(self.sonus)
        self.equalizerWidget = equalizergui.EqualizerWidget(self.sonus)

        self.tabWidget.addTab(self.mlibWidget, self.tr('Media &Library'))
        self.tabWidget.addTab(self.playlistWidget, self.tr('&Playlist'))
        self.tabWidget.addTab(self.collectionsWidget, self.tr('C&ollections'))
        self.tabWidget.addTab(self.equalizerWidget, self.tr('E&qualizer'))
        self.tabWidget.setCurrentIndex(0)
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

    def closeEvent(self, event):
        """
        Reimplemented to handle the close event ourselves, allowing us to
        perform clean up tasks.
        """
        self.emit(SIGNAL('skeletonDialogClosed()'))
        self.hide()