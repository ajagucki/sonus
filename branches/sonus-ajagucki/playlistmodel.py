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
        The 'id' property CANNOT be excluded due to either a bug or a feature
        in the XMMS2 python bindings, otherwise the View breaks. See bug
        report: http://bugs.xmms2.xmms.se/view.php?id=1339
        """
        self.propertiesList = ['id', 'tracknr', 'artist', 'title', 'album']
        if not 'id' in self.propertiesList:
            errMsg = "The 'id' property is not in propertiesList."
            self.logger.error(errMsg)
            raise errMsg

        # FIXME: Setup our connections
        self.connect(self.sonus.playlist,
                     SIGNAL('gotPlaylistIds(PyQt_PyObject)'),
                     self.prepareModelData)
        self.connect(self.sonus.playlist,
                     SIGNAL('searchedMediaInfosPlaylist(PyQt_PyObject)'),
                     self.initModelData)
        self.connect(self.sonus.playlist,
                     SIGNAL('mediaAddedToPlaylist(PyQt_PyObject)'),
                     self.addEntryToModel)
        self.connect(self.sonus.mlib,
                     SIGNAL('SOME_SIGNAL(PyQt_PyObject)'),
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
