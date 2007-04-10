"""
Provides an interface to XMMS2 playlist functions.
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
from xmmsclient import collections as c
import xmmsclient

class Playlist(QObject):
    """
    The Playlist class is used to interface with the XMMS2 playlist API from
    Sonus. It also contains miscellaneous related functions required for use
    by playlistgui.PlaylistWidget.
    """
    def __init__(self, sonus, parent=None):
        QObject.__init__(self, parent)
        self.sonus = sonus
        self.logger = logging.getLogger('Sonus.playlist')

        # Get the current playlist position
        self.sonus.playlist_current_pos('_active', self._playlistPosCb)
        
        # Set callbacks to handle playlist broadcasts.
        self.sonus.broadcast_playlist_changed(self._playlistChangedCb)
        self.sonus.broadcast_playlist_current_pos(self._playlistPosCb)

    def addTrack(self, trackId):
        """
        Adds a track to the playlist.
        """
        self.sonus.playlist_add_id(trackId)

    def remTrack(self, position):
        """
        Removes a track from the playlist.
        """
        self.sonus.playlist_remove_entry(position)

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
        self.logger.debug("oldPos: %s, newPos: %s", oldPos, newPos) 
        self.sonus.playlist_move(oldPos, newPos, '_active', self._moveTrackCb)

    def jump(self, pos):
        """
        Jumps to a specific posistion in the playlist.
        """
        self.sonus.playlist_set_next(pos)
        self.sonus.playback_tickle()

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


    def _getTracksCb(self, xmmsResult):
        """
        Callback for self.getTracks.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s', xmmsResult.get_error())
        else:
            self.emit(SIGNAL('gotPlaylistIds(PyQt_PyObject)'),
                             xmmsResult.value())

    def _playlistClearCb(self, xmmsResult):
        """
        Callback for self.clear.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s', xmmsResult.get_error())

    def _moveTrackCb(self, xmmsResult):
        """
        Callback for self.moveTrack.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s',
                              xmmsResult.get_error())
    
    def _getMediaInfoCb(self, xmmsResult):
        """
        Callback for self.getMediaInfo.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s',
                              xmmsResult.get_error())
        else:
            self.emit(SIGNAL('mediaAddedToPlaylist(PyQt_PyObject)'),
                             xmmsResult.value())

    def _playlistChangedCb(self, xmmsResult):
        """
        Callback for the 'playlist changed' broadcast.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s', xmmsResult.get_error())
        else:
            change = xmmsResult.value()

            # Entry added
            if change["type"] == xmmsclient.PLAYLIST_CHANGED_ADD:
                self.getMediaInfo(change["id"])
            # Entry removed
            elif change["type"] == xmmsclient.PLAYLIST_CHANGED_REMOVE:
                self.emit(SIGNAL('mediaRemovedFromPlaylist(PyQt_PyObject)'),
                          change["position"])
            # Playlist cleared
            elif change["type"] == xmmsclient.PLAYLIST_CHANGED_CLEAR:
                self.emit(SIGNAL('playlistCleared()'))
            # Playlist shuffled
            elif change["type"] == xmmsclient.PLAYLIST_CHANGED_SHUFFLE:
                self.getTracks()

    def _playlistPosCb(self, xmmsResult):
        """
        Callback for the 'playlist current position' broadcast.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s', xmmsResult.get_error())
        else:
            self.emit(SIGNAL('playlistCurrentPos(PyQt_PyObject)'),
                             xmmsResult.value())
