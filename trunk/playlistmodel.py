"""
playlistmodel: Playlist model for playlistgui.PlaylistDialog's QTableView
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

        # FIXME: Setup our connections
        self.connect(self.sonus.playlist,
                     SIGNAL('gotPlaylistIds(PyQt_PyObject)'),
                     self.prepareModelData)
        self.connect(self.sonus.playlist,
                     SIGNAL('searchedMediaInfosPlaylist(PyQt_PyObject)'),
                     self.initModelData)
        self.connect(self.sonus.playlist,
                     SIGNAL('mediaAddedToPlaylist(PyQt_PyObject)'),
                     self.addOrUpdateEntry)
        #FIXME: Need to add method to remove entries from the model 
        self.connect(self.sonus.playlist,
                     SIGNAL('entryRemovedFromPlaylist(PyQy_PyObject)'),
                     None)
        #FIXME: Need to accept list in this signal
        self.connect(self.sonus.playlist,
                     SIGNAL('playlistShuffled()'),
                     self.replaceModelData)
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
        self.sonus.playlist.getMediaInfoPlaylist(newInfoList,
                                                 self.propertiesList)

        # We only prepare once, so ignore future signals.
        self.disconnect(self.sonus.playlist,
                        SIGNAL('gotPlaylistIds(PyQt_PyObject)'),
                        self.prepareModelData)

    def initModelData(self, newInfoList):
        """
        Sets up data for the data that the model provides to a current
        copy from mlib.
        """
        self.replaceModelData(newInfoList)
        self.emit(SIGNAL('modelInitialized()'))

        # We only initialize once, so stop monitoring this signal.
        self.disconnect(self.sonus.playlist,
                        SIGNAL('searchedMediaInfosPlaylist(PyQt_PyObject)'),
                        self.initModelData)
