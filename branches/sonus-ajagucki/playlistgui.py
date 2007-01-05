"""
playlistgui: Playlist dialog
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import playlistmodel

class PlaylistDialog(QDialog):
    """
    The PlaylistDialog class defines the Sonus playlist GUI
    """
    def __init__(self, sonus, parent=None):
        QDialog.__init__(self, parent)

        self.logger = logging.getLogger('Sonus.playlistgui')
        self.sonus = sonus

        self.setWindowTitle(self.tr('Sonus - Playlist'))
        self.resize(QSize(640, 360))

        self.model = playlistmodel.PlaylistModel(self.sonus, self)

        self.gridLayout = QGridLayout(self)

        self.tableView = QTableView(self)
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setShowGrid(False)
        self.tableView.setTabKeyNavigation(False)
        self.tableView.setFocusPolicy(Qt.NoFocus)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.verticalHeader().setDefaultSectionSize(20)
        self.tableView.verticalHeader().setResizeMode(QHeaderView.Fixed)
        self.tableView.verticalHeader().hide()
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.tableView, 1, 0, 1, 3)

        self.removeButton = QPushButton(self)
        self.removeButton.setText(self.tr('&Remove'))
        self.removeButton.setAutoDefault(False)

        self.shuffleButton = QPushButton(self)
        self.shuffleButton.setText(self.tr('&Shuffle'))
        self.shuffleButton.setAutoDefault(False)

        self.clearButton = QPushButton(self)
        self.clearButton.setText(self.tr('&Clear'))
        self.clearButton.setAutoDefault(False)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.addButton(self.shuffleButton,
                                  QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.removeButton,
                                  QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.clearButton,
                                  QDialogButtonBox.ActionRole)
        self.gridLayout.addWidget(self.buttonBox, 2, 1, 1,1)

        self.repeatAll = QCheckBox(self.tr('Repeat &all'), self)
        self.gridLayout.addWidget(self.repeatAll, 2, 0, 1, 1)

        self.connect(self.shuffleButton, SIGNAL('clicked()'),
                     self.sonus.playlist.shuffle)
        self.connect(self.removeButton, SIGNAL('clicked()'),
                     self._removeTrackCb)
        self.connect(self.clearButton, SIGNAL('clicked()'),
                     self.sonus.playlist.clear)
        self.connect(self.repeatAll, SIGNAL('clicked()'),
                     self.updateRepeatAll)
        self.connect(self.model, SIGNAL('modelInitialized()'),
                     self.initView)

    def initView(self):
        """
        Initializes the view, setting its model.
        """
        self.tableView.setModel(self.model)

    def reject(self):
        """
        Effectively ignores calls to reject(), in case the user presses the
        escape key. The only reason this class is a QDialog is to allow
        detachment in the future.
        """
        pass

    def _removeTrackCb(self, position=None):
        """
        Removes selected track from the playlist
        """
        self.logger.debug('_removeTrackCb() called')

    def updateRepeatAll(self):
        """
        Toggles playlist repeat
        """
        if self.repeatAll.checkState():
            self.sonus.playlist.repeat_all(1)
        else:
            self.sonus.playlist.repeat_all(0)
