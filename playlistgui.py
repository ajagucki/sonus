"""
playlistgui: Playlist dialog
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class PlaylistDialog(QDialog):
    def __init__(self, sonus, parent=None):
        QDialog.__init__(self, parent)

        self.logger = logging.getLogger('Sonus.mlibgui')
        self.sonus = sonus
        
        self.grid_layout = QGridLayout(self)
        
        self.table_view = QTableView(self)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setShowGrid(False)
        self.table_view.setTabKeyNavigation(False)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.verticalHeader().hide()
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.grid_layout.addWidget(self.table_view, 1, 0, 1, 3)
        
        self.remove_button = QPushButton(self)
        self.remove_button.setText(self.tr('&Remove'))
        self.remove_button.setAutoDefault(False)
        
        self.shuffle_button = QPushButton(self)
        self.shuffle_button.setText(self.tr('&Shuffle'))
        self.shuffle_button.setAutoDefault(False)
        
        self.button_box = QDialogButtonBox(self)
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.addButton(self.shuffle_button,
                                  QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.remove_button,
                                  QDialogButtonBox.ActionRole)
        self.grid_layout.addWidget(self.button_box, 2, 1, 1,1)