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

    def mimeTypes(self):
        """
        Encodes items with proper MIME type.
        """
        # Useing same MIME type as Esperanza.
        typeList = QStringList("application/x-xmms2poslist")
        return typeList
    
    def mimeData(self, indexes):
        """
        Encodes the data in specified format.
        """
        mimeData = QMimeData()
        encodedData = QByteArray()
        rowFlag = 0

        stream = QDataStream(encodedData, QIODevice.WriteOnly)

        for index in indexes:
            if index.isValid():
                text = self.data(index, Qt.DisplayRole).toString()
                stream << text
                rowFlag += 1
                if rowFlag == len(self.propertiesList):
                    stream << QString.number(index.row())
                    rowFlag = 0

        mimeData.setData('application/x-xmms2poslist', encodedData)
        return mimeData
    
    def dropMimeData(self, data, action, row, column, parent):
        """
        Handles entries being dropped.
        """
        if action == Qt.IgnoreAction:
            return True
        
        if not data.hasFormat("application/x-xmms2poslist"):
            return False

        if column > 0:
            return False

        if row != -1:
            beginRow = row
        elif parent.isValid():
            beginRow = parent.row()
        else:
            beginRow = self.rowCount(QModelIndex())

        encodedData = QByteArray(data.data('application/x-xmms2poslist'))
        stream = QDataStream(encodedData, QIODevice.ReadOnly)
        newItems = QStringList()
        text = QString()
        rows = 0
        col = 0
        
        while stream.status() != QDataStream.ReadPastEnd:
            stream >> text
            newItems << text
            rows += 1

        N = len(self.propertiesList)
        rows = rows / N
        self.insertRows(beginRow, rows)
        newItems.removeAt(len(newItems) - 1)
        
        rowList = newItems[N::N + 1]
        del newItems[N::N + 1]
        
        iteration = 0
        for text in newItems:
            idx = self.index(beginRow, col)
            self.setData(idx, text, Qt.DisplayRole)
            col += 1
            if col == N:
                self.sonus.playlist.moveTrack(int(rowList[iteration]), beginRow)
                beginRow += 1
                iteration += 1
                col = 0
        
        return True