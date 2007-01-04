"""
playlistmodel: Playlist model for playlistgui.PlaylistDialog's QTableView
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *

from supermodel import *


class PlaylistModel(SuperModel):
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
        self.properties_list = ['id', 'tracknr', 'artist', 'title', 'album']
        if not 'id' in self.properties_list:
            err_msg = "The 'id' property is not in properties_list."
            self.logger.error(err_msg)
            raise err_msg

        # FIXME: Setup our connections
        self.connect(self.sonus.playlist,
                     SIGNAL('got_playlist_ids(PyQt_PyObject)'),
                     self.prepareModelData)
        self.connect(self.sonus.playlist,
                     SIGNAL('searched_media_infos_playlist(PyQt_PyObject)'),
                     self.initModelData)
        self.connect(self.sonus.playlist, SIGNAL('SOME_SIG(PyQt_PyObject)'),
                     self.addEntryToModel)
        self.connect(self.sonus.mlib,
                     SIGNAL('SOME_SIGNAL(PyQt_PyObject)'),
                     self.replaceModelData)

        # Initiaize our data
        self.sonus.playlist.get_tracks()

    def prepareModelData(self, new_info_list):
        """
        Sets up data for the data that the model provides to a current
        copy from mlib.
        """
        self.sonus.playlist.get_media_info_playlist(new_info_list, self.properties_list)

        # We only prepare once, so ignore future signals.
        self.disconnect(self.sonus.playlist,
                        SIGNAL('got_playlist_ids(PyQt_PyObject)'),
                        self.prepareModelData)

    def initModelData(self, new_info_list):
        """
        Sets up data for the data that the model provides to a current
        copy from mlib.
        """
        self.entry_info_list = new_info_list
        self.emit(SIGNAL('model_initialized()'))

        # We only initialize once, so ignore future signals.
        self.disconnect(self.sonus.playlist,
                        SIGNAL('got_playlist_ids(PyQt_PyObject)'),
                        self.initModelData)