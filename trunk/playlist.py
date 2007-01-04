"""
playlist: Interacts with the XMMS2 playlist functions.
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
import xmmsclient


class Playlist(QObject):
    def __init__(self, sonus, parent=None):
        QObject.__init__(self, parent)
        self.sonus = sonus
        self.logger = logging.getLogger('Sonus.playlist')

    def add_track(self, track_id):
        self.sonus.playlist_add_id(track_id)

    def rem_track(self, position):
        self.sonus.playlist_remove(position)

    def insert_track(self, track_id, position):
        self.sonus.playlist_insert_id(postion, track_id)

    def move_track(self, old_pos, new_pos):
        self.sonus.playlist_move(old_pos, new_pos)

    def repeat_one(self, bool):
        self.sonus.configval_set('playlist.repeat_one', str(bool))

    def repeat_all(self, bool):
        self.sonus.configval_set('playlist.repeat_all', str(bool))

    def shuffle(self):
        self.sonus.playlist_shuffle()

    def clear(self):
        self.sonus.playlist_clear("_active", self._playlist_clear_cb)

    def get_tracks(self):
        """
        Gets a list of IDs currently in the playlist.
        """
        self.sonus.playlist_list_entries("_active", self._get_tracks_cb)

    def get_media_info_playlist(self, entry_ids, properties_list):
        """
        Queries for track information for a given media library entry id.
        Playlist specific.
        """
        match_query = xmmsclient.Universe()
        match_query &= xmmsclient.Match(field='id', value='')   # Null set
        for track_id in entry_ids:
            match_query |= xmmsclient.Match(field='id', value='%s' % track_id)

        self.sonus.coll_query_infos(match_query, properties_list,
                                    cb=self._search_media_infos_playlist_cb)

    def _get_tracks_cb(self, xmms_result):
        if xmms_result.iserror():
            self.logger.error('XMMS result error: %s', xmms_result.get_error())
        else:
            playlist_track_list = xmms_result.value()
            self.emit(SIGNAL('got_playlist_ids(PyQt_PyObject)'),
                              playlist_track_list)

    def _playlist_clear_cb(self, xmms_result):
        if xmms_result.iserror():
            self.logger.error('XMMS result error: %s', xmms_result.get_error())
        else:
            self.emit(SIGNAL('playlist_cleared()'))

    def _search_media_infos_playlist_cb(self, xmms_result):
        """
        Callback for self.search_media_infos.
        """
        if xmms_result.iserror():
            self.logger.error('XMMS result error: %s', xmms_result.get_error())
        else:
            mlib_info_list = xmms_result.value()
            self.emit(SIGNAL('searched_media_infos_playlist(PyQt_PyObject)'),
                             mlib_info_list)