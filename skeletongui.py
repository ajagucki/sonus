"""
skeletongui: multi-purpose "blank" dialog
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import mlibgui

class SkeletonGui(QDialog):
    def __init__(self, sonus, parent=None):
        QDialog.__init__(self, parent)

        self.logger = logging.getLogger('Sonus.skeletongui')
        self.sonus = sonus

        self.setWindowTitle(self.tr('Sonus - Manager'))
        self.resize(QSize(640, 360))
        self.setSizeGripEnabled(True)
        
        # Encapsulate our modules
        self.mlib_dialog = mlibgui.MlibDialog(self.sonus, self)

        # Create tabs
        self.tab_widget = QTabWidget(self)
        self.tab_widget.resize(QSize(640, 360))
        self.tab_widget.addTab(self.mlib_dialog, self.tr('Media &Library'))
        # TODO: Make tabs resize
