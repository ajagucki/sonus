"""
playlistgui: Playlist dialog
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import playlistmodel

class PlaylistDialog(QDialog):
    def __init__(self, sonus, parent=None):
        QDialog.__init__(self, parent)

        self.logger = logging.getLogger('Sonus.mlibgui')
        self.sonus = sonus
        
        self.setWindowTitle(self.tr('Sonus - Playlist'))
        self.resize(QSize(640, 360))
        self.setSizeGripEnabled(True)
        
        self.model = playlistmodel.PlaylistModel(self.sonus, self)
        
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
        
        self.repeat_all = QCheckBox(self.tr('Repeat &all'), self)
        self.grid_layout.addWidget(self.repeat_all, 2, 0, 1, 1)
        
        self.connect(self.shuffle_button, SIGNAL('clicked()'),
                     self.sonus.playlist.shuffle)
        self.connect(self.remove_button, SIGNAL('clicked()'),
                     self.remove_track_cb)
        self.connect(self.repeat_all, SIGNAL('clicked()'),
                     self.update_repeat_all)
        self.connect(self.model, SIGNAL('model_initialized()'),
                     self.init_view)

    def init_view(self):
        """
        Initializes the view, setting its model.
        """
        self.table_view.setModel(self.model)
    
    def remove_track_cb(self, position=None):
        """
        Removes selected track from the playlist
        """
        self.logger.debug("remove_track_cb() called")

    def update_repeat_all(self):
        """
        Toggles playlist repeat
        """
        if self.repeat_all.checkState():
            self.sonus.playlist.repeat_all(1)
        else:
            self.sonus.playlist.repeat_all(0)