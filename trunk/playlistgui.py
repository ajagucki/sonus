"""
Playlist graphical user interface.
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import playlistmodel


class PlaylistDialog(QDialog):
    """
    The PlaylistDialog class defines the Sonus playlist GUI.
    """
    def __init__(self, sonus, parent=None):
        """
        PlaylistDialog's constructor creates all of its widgets, sets up their
        connections, and performs other initializations.
        """
        QDialog.__init__(self, parent)

        self.logger = logging.getLogger('Sonus.playlistgui')
        self.sonus = sonus

        self.setWindowTitle(self.tr('Sonus - Playlist'))
        self.resize(QSize(640, 360))

        self.model = playlistmodel.PlaylistModel(self.sonus, self)

        self.gridLayout = QGridLayout(self)

        self.treeView = QTreeView(self)
        self.treeView.setRootIsDecorated(False)
        self.treeView.setItemsExpandable(False)
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.gridLayout.addWidget(self.treeView, 1, 0, 1, 3)

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
        self.sonus.configval_get('playlist.repeat_all', self._repeatAllCb)
        self.gridLayout.addWidget(self.repeatAll, 2, 0, 1, 1)
        
        self.popUp = QMenu(self.treeView)
        # Need to make these do things
        self.popUp.addAction(self.tr('Save'))
        self.popUp.addAction(self.tr('Load'))

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
        self.connect(self.treeView,
                     SIGNAL('customContextMenuRequested(QPoint)'),
                     self.popUpMenu)
    
    def initView(self):
        """
        Initializes the view, setting its model.
        """
        self.treeView.setModel(self.model)

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
            self.sonus.playlist.repeatAll(1)
        else:
            self.sonus.playlist.repeatAll(0)

    def _repeatAllCb(self, xmmsResult):
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s', xmmsResult.get_error())
        elif xmmsResult.value() == "1":
            self.repeatAll.setCheckState(Qt.Checked)
    
    def savePlaylist(self):
        self.logger.debug('savePlaylist() called')

    def loadPlatlist(self):
        self.logger.debug('loadPlaylist() called')

    def popUpMenu(self):
        self.popUp.popup(QCursor.pos())
