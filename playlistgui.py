"""
Playlist graphical user interface.
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import playlistmodel


class PlaylistWidget(QWidget):
    """
    The PlaylistWidget class defines the Sonus playlist GUI.
    """
    def __init__(self, sonus, parent=None):
        """
        PlaylistWidget's constructor creates all of its widgets, sets up their
        connections, and performs other initializations.
        """
        QWidget.__init__(self, parent)

        self.logger = logging.getLogger('Sonus.playlistgui')
        self.sonus = sonus

        self.setWindowTitle(self.tr('Sonus - Playlist'))
        self.resize(QSize(640, 360))

        self.model = playlistmodel.PlaylistModel(self.sonus, self)

        self.gridLayout = QGridLayout(self)

        self.treeView = TreeView(self)
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
        self.buttonBox.addButton(self.clearButton, QDialogButtonBox.ActionRole)
        self.gridLayout.addWidget(self.buttonBox, 2, 1, 1, 1)

        self.repeatAll = QCheckBox(self.tr('Repeat &all'), self)
        self.sonus.configval_get('playlist.repeat_all', self._repeatAllCb)
        self.gridLayout.addWidget(self.repeatAll, 2, 0, 1, 1)

        self.popUp = QMenu(self.treeView)
        # Need to make these do things
        self.popUp.addAction(self.tr('Save'))
        self.popUp.addAction(self.tr('Load'))
        self.popUp.addAction(self.tr('New'))

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
        self.connect(self.model,
                     SIGNAL('trackMoved(PyQt_PyObject, PyQt_PyObject)'),
                     self.sonus.playlist.moveTrack)
        self.connect(self.treeView,
                     SIGNAL('customContextMenuRequested(QPoint)'),
                     self.popUpMenu)
        self.connect(self.treeView, SIGNAL('doubleClicked(QModelIndex)'),
                     self.doubleClick)
        self.connect(self.sonus.playlist,
                     SIGNAL('playlistCurrentPos(PyQt_PyObject)'),
                     self._currentPosCb)

    def initView(self):
        """
        Initializes the view, setting its model.
        """
        self.treeView.setModel(self.model)

    def _removeTrackCb(self):
        """
        Removes selected track from the playlist
        """
        selectionModel = self.treeView.selectionModel()
        indexes = selectionModel.selectedIndexes()
        
        """
        We get N indexes for every row, so we need to iterate though
        to get one index per row. We then need to sort them so that
        the tracks are deleted in ascending order to avoid problems
        with positions changing.
        """
        N = len(self.model.propertiesList)
        rows = [indexes[i].row() for i in range(0, len(indexes), N)]
        rows.sort(reverse=True)
        
        for row in rows:
            self.sonus.playlist.remTrack(row)

    def updateRepeatAll(self):
        """
        Toggles playlist repeat
        """
        if self.repeatAll.checkState():
            self.sonus.playlist.repeatAll(1)
        else:
            self.sonus.playlist.repeatAll(0)

    def _repeatAllCb(self, xmmsResult):
        """
        Toggles the 'repeat all' checkbox if needed.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s', xmmsResult.get_error())
        elif xmmsResult.value() == "1":
            self.repeatAll.setCheckState(Qt.Checked)

    def savePlaylist(self):
        """
        Saves current playlist.
        """
        self.logger.debug('savePlaylist() called')

    def loadPlatlist(self):
        """
        Loads a specified playlist.
        """
        self.logger.debug('loadPlaylist() called')

    def popUpMenu(self):
        """
        Pops up the playlist save/load popup menu.
        """
        self.popUp.popup(QCursor.pos())

    def doubleClick(self, mediaIndex):
        """
        Jumps to double clicked track
        """
        if not mediaIndex.isValid():
            self.logger.error('Got invalid index.')
            return

        self.sonus.playlist.jump(mediaIndex.row())

    def _currentPosCb(self, pos):
        self.logger.debug('Current position: %s', pos)
        #TODO: Get index and change row color

class TreeView(QTreeView):
    """
    Custom QTreeView widget.
    """
    def __init__(self, parent):
        """
        Initializes the view.
        """
        QTreeView.__init__(self, parent)
        
        self.logger = logging.getLogger('Sonus.playlistgui')
        self.parent = parent
        
        self.setRootIsDecorated(False)
        self.setItemsExpandable(False)
        self.setAlternatingRowColors(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
    
    def keyPressEvent(self, event):
        """
        Handles keypresses.
        """
        if event.key() == Qt.Key_Delete:
            self.parent._removeTrackCb()