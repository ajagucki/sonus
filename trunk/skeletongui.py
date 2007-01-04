"""
skeletongui: multi-purpose "blank" dialog
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import mlibgui
import playlistgui

class SkeletonDialog(QDialog):
    def __init__(self, sonus, parent=None):
        QDialog.__init__(self, parent)

        self.logger = logging.getLogger('Sonus.skeletongui')
        self.sonus = sonus

        self.setWindowTitle(self.tr('Sonus - Manager'))
        self.resize(QSize(640, 360))

        self.grid_layout = QGridLayout(self)

        self.tab_widget = QTabWidget(self)
        self.mlib_dialog = mlibgui.MlibDialog(self.sonus)
        self.playlist_dialog = playlistgui.PlaylistDialog(self.sonus)
        self.tab_widget.addTab(self.mlib_dialog, self.tr('Media &Library'))
        self.tab_widget.addTab(self.playlist_dialog, self.tr('&Playlist'))
        self.grid_layout.addWidget(self.tab_widget, 0, 0, 1, 1)
        self.tab_widget.setCurrentIndex(0)
