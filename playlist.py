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

        # Set a callback to handle an 'playlist changed' broadcast.
        self.sonus.broadcast_playlist_changed(self._playlistChangedCb)

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
        self.sonus.playlist_clear('_active', self._playlist_clear_cb)

    def get_tracks(self):
        """
        Gets a list of IDs currently in the playlist.
        """
        self.sonus.playlist_list_entries('_active', self._get_tracks_cb)

    def get_media_info(self, entry_id):
        """
        Queries for track information for a given media library entry id.
        """
        self.sonus.medialib_get_info(entry_id, self._get_media_info_cb)

    def get_media_info_playlist(self, entry_id_list, properties_list):
        """
        Queries for track information for a given media library entry id.
        Playlist specific.
        """
        search_query = xmmsclient.Universe()
        search_query &= xmmsclient.Match(field='id', value='')  # Null set
        for entry_id in entry_id_list:
            search_query |= xmmsclient.Match(field='id', value='%s' % entry_id)

        self.sonus.coll_query_infos(search_query, properties_list,
                                    cb=self._search_media_infos_playlist_cb)

    def _get_tracks_cb(self, xmms_result):
        if xmms_result.iserror():
            self.logger.error('XMMS result error: %s',
                              xmms_result.get_error())
        else:
            playlist_track_list = xmms_result.value()
            self.emit(SIGNAL('got_playlist_ids(PyQt_PyObject)'),
                             playlist_track_list)

    def _playlist_clear_cb(self, xmms_result):
        if xmms_result.iserror():
            self.logger.error('XMMS result error: %s',
                              xmms_result.get_error())
        else:
            self.emit(SIGNAL('playlist_cleared()'))

    def _search_media_infos_playlist_cb(self, xmms_result):
        """
        Callback for self.search_media_infos.
        """
        if xmms_result.iserror():
            self.logger.error('XMMS result error: %s',
                              xmms_result.get_error())
        else:
            mlib_info_list = xmms_result.value()
            self.emit(SIGNAL('searched_media_infos_playlist(PyQt_PyObject)'),
                             mlib_info_list)

    def _get_media_info_cb(self, xmms_result):
        """
        Callback for self.get_media_info.
        """
        if xmms_result.iserror():
            self.logger.error('XMMS result error: %s', xmms_result.get_error())
        else:
            mlib_info_entry = xmms_result.value()
            self.emit(SIGNAL('media_added_to_playlist(PyQt_PyObject)'),
                             mlib_info_entry)

    def _playlistChangedCb(self, xmms_result):
        if xmms_result.iserror():
            self.logger.error('XMMS result error: %s', xmms_result.get_error())
        else:
            change = xmms_result.value()

            # Itam added
            if change["type"] == xmmsclient.PLAYLIST_CHANGED_ADD:
                self.get_media_info(change["id"])
