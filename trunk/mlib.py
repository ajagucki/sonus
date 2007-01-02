"""
mlib: Interacts with the XMMS2 medialib functions.
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
import xmmsclient


class Mlib(QObject):
    def __init__(self, sonus, parent=None):
        QObject.__init__(self, parent)
        self.sonus = sonus
        self.logger = logging.getLogger('Sonus.mlib')

        """
        An incomplete dictionary of properties as defined in the XMMS2 source
        code: src/include/xmms/xmms_medialib.h
        """
        self.properties_dict = {
            'title':'Title',
            'artist':'Artist',
            'album':'Album',
            'tracknr':'Track',
            'duration':'Length',
            'id':'ID',
        }

        # Set a callback to handle an 'entry added' broadcast.
        #self.sonus.broadcast_medialib_entry_added(self.entry_added_cb)
        self.sonus.broadcast_medialib_entry_changed(self.entry_changed_cb)
        self.ignore_future_cb = False

    def get_all_media_infos(self, properties_list):
        """
        Queries for a list of information for all tracks in the media library.
        """
        self.sonus.coll_query_infos(xmmsclient.Universe(), properties_list,
                                    cb=self.infos_query_cb)

    def get_media_info(self, entry_id):
        """
        Queries for track information for a given media library entry id.
        """
        self.sonus.medialib_get_info(entry_id, self.info_query_cb)

    def get_matching_media_infos(self, search_type, search_string,
                                 properties_list):
        """
        Queries for a list of information for tracks in the media library
        matching a specific field and value pair.
        """
        self.logger.debug('get_matching_media_infos() not implemented.')
        """
        if search_type == 'Artist':
            match_query = xmmsclient.Match(Artist="buckethead")
        elif search_type == 'Title':
            match_query = xmmsclient.Match(title=search_string)
        elif search_type == 'Album':
            match_query = xmmsclient.Match(album=search_string)
        else:
            match_query = xmmsclient.Match()
            self.logger.debug('Cannot handle search_type: ' + search_type)

        self.sonus.coll_query_infos(match_query, properties_list,
                                    cb=self.infos_query_cb)
        """

    def infos_query_cb(self, xmms_result):
        """
        Callback for a collection query returning a list of track information.
        """
        if xmms_result.iserror():
            self.logger.error('XMMS result error: %s', xmms_result.get_error())
        else:
            mlib_info_list = xmms_result.value()
            self.emit(SIGNAL('got_all_media_infos(PyQt_PyObject)'),
                             mlib_info_list)

    def info_query_cb(self, xmms_result):
        """
        Callback for a media library query returning track information for
        a single entry.
        """
        if xmms_result.iserror():
            self.logger.error('XMMS result error: %s', xmms_result.get_error())
        else:
            mlib_info_entry = xmms_result.value()
            self.emit(SIGNAL('got_media_info(PyQt_PyObject)'), mlib_info_entry)


    def entry_added_cb(self, xmms_result):
        """
        Callback for the media library 'entry added' broadcast.
        """
        if xmms_result.iserror():
            self.logger.error('XMMS result error: %s', xmms_result.get_error())
        else:
            entry_id = xmms_result.value()
            self.logger.info('Entry %s added to the media library.', entry_id)
            self.get_media_info(entry_id)

    def entry_changed_cb(self, xmms_result):
        """
        Callback for the media library 'entry changed' broadcast.
        """
        if self.ignore_future_cb == True:
            self.logger.debug('Ignored entry_changed_cb.')
            self.ignore_future_cb = False
            return
        if xmms_result.iserror():
            self.logger.error('XMMS result error: %s', xmms_result.get_error())
        else:
            entry_id = xmms_result.value()
            self.logger.info('Entry %s changed in media library.', entry_id)
            self.get_media_info(entry_id)
            self.ignore_future_cb = True
