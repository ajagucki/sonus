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
        self.sonus.broadcast_medialib_entry_added(self.entry_added_cb)
        self.sonus.broadcast_medialib_entry_changed(self.entry_changed_cb)
        self.ignoring_future_cb = False
        self.entry_was_added = False

    def get_all_media_infos(self, properties_list):
        """
        Queries for a list of information for all tracks in the media library.
        """
        self.sonus.coll_query_infos(xmmsclient.Universe(), properties_list,
                                    cb=self._get_all_media_infos_cb)

    def get_media_info(self, entry_id):
        """
        Queries for track information for a given media library entry id.
        """
        self.sonus.medialib_get_info(entry_id, self._get_media_info_cb)

    def search_media_infos(self, search_type, search_string,
                                 properties_list):
        """
        Queries for a list of information for tracks in the media library
        matching a specific field and value pair.
        """
        if search_type == 'All':
            match_query = xmmsclient.Match(field='id', value='%')   # Null set
            for property in properties_list:
                    match_query |= xmmsclient.Contains(field=property,
                                                       value=search_string)
        else:
            for key, value in self.properties_dict.items():
                if search_type == value:
                    match_query = xmmsclient.Contains(field=key,
                                                      value=search_string)
                    break
            else:
                match_query = xmmsclient.Contains()
                self.logger.error('Cannot handle search_type: %s', search_type)
                return

        self.logger.info("Searching media library under '%s' for '%s'",
                         search_type, search_string)
        self.sonus.coll_query_infos(match_query, properties_list,
                                    cb=self._search_media_infos_cb)

    def _get_all_media_infos_cb(self, xmms_result):
        """
        Callback for self.get_all_media_infos.
        """
        if xmms_result.iserror():
            self.logger.error('XMMS result error: %s', xmms_result.get_error())
        else:
            mlib_info_list = xmms_result.value()
            self.emit(SIGNAL('got_all_media_infos(PyQt_PyObject)'),
                             mlib_info_list)

    def _get_media_info_cb(self, xmms_result):
        """
        Callback for self.get_media_info.
        """
        if xmms_result.iserror():
            self.logger.error('XMMS result error: %s', xmms_result.get_error())
        else:
            mlib_info_entry = xmms_result.value()
            self.emit(SIGNAL('got_media_info(PyQt_PyObject)'), mlib_info_entry)

    def _search_media_infos_cb(self, xmms_result):
        """
        Callback for self.search_media_infos.
        """
        if xmms_result.iserror():
            self.logger.error('XMMS result error: %s', xmms_result.get_error())
        else:
            mlib_info_list = xmms_result.value()
            self.emit(SIGNAL('searched_media_infos(PyQt_PyObject)'),
                             mlib_info_list)

    def entry_added_cb(self, xmms_result):
        """
        Callback for the media library 'entry added' broadcast.
        """
        if xmms_result.iserror():
            self.logger.error('XMMS result error: %s', xmms_result.get_error())
        else:
            self.entry_was_added = True
            entry_id = xmms_result.value()
            self.logger.info('Entry %s added to the media library.', entry_id)
            #self.get_media_info(entry_id)

    def entry_changed_cb(self, xmms_result):
        """
        Callback for the media library 'entry changed' broadcast.
        """
        if self.ignoring_future_cb == True:
            self.ignore_future_cb = False
            return
        if xmms_result.iserror():
            self.logger.error('XMMS result error: %s', xmms_result.get_error())
        else:
            if self.entry_was_added == True:
                entry_id = xmms_result.value()
                self.logger.info('Entry %s changed in media library.',
                                 entry_id)
                self.get_media_info(entry_id)
                self.ignore_future_cb = True
                self.entry_was_added = False
