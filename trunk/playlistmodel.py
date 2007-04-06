"""
playlistmodel: Playlist model for playlistgui.PlaylistWidget's QTableView
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *

from supermodel import *

class PlaylistModel(SuperModel):
    """
    The PlaylistModel class handles the playlist model. This includes
    initializing it and handling the signals that keep it up to date.
    """
    def __init__(self, sonus, parent=None):
        SuperModel.__init__(self, parent)
        self.sonus = sonus
        self.logger = logging.getLogger('Sonus.playlistmodel')

        """
        The list of properties to return from XMMS2 queries.
        The order of the horizontal header sections reflects the order of the
        properties in this list.
        """
        self.propertiesList = ['tracknr', 'artist', 'title', 'album']

        # Setup our connections
        self.connect(self.sonus.playlist,
                     SIGNAL('gotPlaylistIds(PyQt_PyObject)'),
                     self.prepareModelData)
        self.connect(self.sonus.collections,
                     SIGNAL('gotCollInfosPlaylist(PyQt_PyObject)'),
                     self.initModelData)
        self.connect(self.sonus.playlist,
                     SIGNAL('mediaAddedToPlaylist(PyQt_PyObject)'),
                     self.addOrUpdateEntry)
	self.connect(self.sonus.playlist,
                     SIGNAL('mediaRemovedFromPlaylist(PyQt_PyObject)'),
                     self.removeRows)	
        self.connect(self.sonus.playlist,
                     SIGNAL('playlistCleared()'),
                     self.replaceModelData)

        # Initiaize our data
        self.sonus.playlist.getTracks()

    def prepareModelData(self, newInfoList):
        """
        Sets up data for the data that the model provides to a current
        copy from mlib.
        """
        self.sonus.collections.getCollInfoPlaylist(newInfoList,
                                                   self.propertiesList)

    def initModelData(self, newInfoList):
        """
        Sets up data for the data that the model provides to a current
        copy from mlib.
        """
        self.replaceModelData(newInfoList)
        self.emit(SIGNAL('modelInitialized()'))

    def supportedDropActions(self):
        """
        Let the view know which actions are supported.
        """
        return Qt.MoveAction | Qt.CopyAction

    def flags(self, index):
        """
        Model tells the view which items can be dragged and dropped.
        """
        defaultFlags = QAbstractTableModel.flags(self, index)

        if index.isValid():
            return Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | defaultFlags
        else:
            return Qt.ItemIsDropEnabled | defaultFlags

    def dropMimeData(self, data, action, row, column, parent):
        """
        Handles entries being dropped.
        """
        if action == Qt.IgnoreAction:
            return True
        if column > 0:
            return False

        if row != -1:
            beginRow = row
        elif parent.isValid():
            beginRow = parent.row()
        else:
            beginRow = self.rowCount(QModelIndex())

        self.emit(SIGNAL('trackMoved(PyQt_PyObject, PyQt_PyObject)'),
                  row, beginRow)

        self.insertRows(beginRow)
        index = self.index(beginRow, 0)
        text = self.data(self.index(row, 0), Qt.DisplayRole).toString()
        self.logger.debug("Text: %s", text)
        #self.setData(index, text, Qt.DisplayRole)
        
        return True
            