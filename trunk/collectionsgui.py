"""
Collections graphical user interface.
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class CollectionsDialog(QDialog):
    """
    The CollectionsDialog class defines the Sonus collections GUI.
    """
    def __init__(self, sonus, parent=None):
        """
        PlaylistDialog's constructor creates all of its widgets, sets up their
        connections, and performs other initializations.
        """
        QDialog.__init__(self, parent)

        self.logger = logging.getLogger('Sonus.collectionsgui')
        self.sonus = sonus

        self.setWindowTitle(self.tr('Sonus - Collections'))
        self.resize(QSize(640, 360))