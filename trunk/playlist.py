"""
playlist: Interacts with the XMMS2 playlist functions.
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
import xmmsclient


class Playlist(QObject):
    """
    The Playlist class is used to interface with the XMMS2 playlist API from
    Sonus. It also contains miscellaneous related functions required for the
    interface to work properly.
    """
    def __init__(self, sonus, parent=None):
        QObject.__init__(self, parent)
        self.sonus = sonus
        self.logger = logging.getLogger('Sonus.playlist')

        # Set a callback to handle an 'playlist changed' broadcast.
        self.sonus.broadcast_playlist_changed(self._playlistChangedCb)

    def addTrack(self, trackId):
        """
        Adds a track to the playlist.
        """
        self.sonus.playlist_add_id(trackId)

    def remTrack(self, position):
        """
        Removes a track from the playlist.
        """
        self.sonus.playlist_remove(position)

    def insertTrack(self, trackId, position):
        """
        Inserts a track into the playlist at a specified position.
        """
        self.sonus.playlist_insert_id(postion, trackId)

    def moveTrack(self, oldPos, newPos):
        """
        Moves a track from a specified posistion in that playlist to a new
        specified position.
        """
        self.sonus.playlist_move(oldPos, newPos)

    def repeatOne(self, bool):
        """
        Toggles the XMMS2 playlist.repeat_one configval.
        """
        self.sonus.configval_set('playlist.repeat_one', str(bool))

    def repeatAll(self, bool):
        """
        Toggles the XMMS2 playlist.repeat_all configval.
        """
        self.sonus.configval_set('playlist.repeat_all', str(bool))

    def shuffle(self):
        """
        Shuffles the playlist.
        """
        self.sonus.playlist_shuffle()

    def clear(self):
        """
        Clears the playlist
        """
        self.sonus.playlist_clear('_active', self._playlistClearCb)

    def getTracks(self):
        """
        Gets a list of IDs currently in the playlist.
        """
        self.sonus.playlist_list_entries('_active', self._getTracksCb)

    def getMediaInfo(self, entryId):
        """
        Queries for track information for a given media library entry id.
        """
        self.sonus.medialib_get_info(entryId, self._getMediaInfoCb)

    def getMediaInfoPlaylist(self, entryIdList, propertiesList):
        """
        Queries for track information for a given media library entry id.
        Playlist specific.
        """
        searchQuery = xmmsclient.Universe()
        searchQuery &= xmmsclient.Match(field='id', value='')  # Null set
        for entryId in entryIdList:
            searchQuery |= xmmsclient.Match(field='id', value='%s' % entryId)

        self.sonus.coll_query_infos(searchQuery, propertiesList,
                                    cb=self._searchMediaInfosPlaylistCb)

    def _getTracksCb(self, xmmsResult):
        """
        Callback for self.getTracks.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s',
                              xmmsResult.get_error())
        else:
            playlistTrackList = xmmsResult.value()
            self.emit(SIGNAL('gotPlaylistIds(PyQt_PyObject)'),
                             playlistTrackList)

    def _playlistClearCb(self, xmmsResult):
        """
        Callback for self.clear.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s',
                              xmmsResult.get_error())
        else:
            self.emit(SIGNAL('playlistCleared()'))

    def _searchMediaInfosPlaylistCb(self, xmmsResult):
        """
        Callback for self.search_media_infos.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s',
                              xmmsResult.get_error())
        else:
            mlibInfoList = xmmsResult.value()
            self.emit(SIGNAL('searchedMediaInfosPlaylist(PyQt_PyObject)'),
                             mlibInfoList)

    def _getMediaInfoCb(self, xmmsResult):
        """
        Callback for self.get_media_info.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s',
                              xmmsResult.get_error())
        else:
            mlibInfoEntry = xmmsResult.value()
            self.emit(SIGNAL('mediaAddedToPlaylist(PyQt_PyObject)'),
                             mlibInfoEntry)

    def _playlistChangedCb(self, xmmsResult):
        """
        Callback for the 'playlist changed' broadcast.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s',
                              xmmsResult.get_error())
        else:
            change = xmmsResult.value()

            # Item added
            if change["type"] == xmmsclient.PLAYLIST_CHANGED_ADD:
                self.getMediaInfo(change["id"])
