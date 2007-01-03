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

    def get_tracks(self):
        """
        Going to want to send this back in a signal for the GUI.
        """
        self.sonus.playlist_list(self._get_tracks_cb)

    def _get_tracks_cb(self, xmms_result):
        if xmms_result.iserror():
            self.logger.error('XMMS result error: %s', xmms_result.get_error())
        else:
            playlist_track_list = xmms_result.value()
            self.emit(SIGNAL('got_playlist_tracks(PyQt_PyObject)'),
                              playlist_track_list)
