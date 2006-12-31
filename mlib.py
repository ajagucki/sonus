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
        self.logger = logging.getLogger('sonusLogger.mlib.Mlib')
        self.all_media = xmmsclient.Universe()

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

    def get_all_media_ids(self):
        """
        Queries for a list of all the track IDs in the media library.
        """
        self.sonus.coll_query_ids(self.all_media, cb=self.ids_query_cb)

    def get_all_media_infos(self, properties_list):
        """
        Queries for a list of information for all tracks in the media library.
        """
        self.sonus.coll_query_infos(self.all_media, properties_list,
                                    cb=self.infos_query_cb)

    def get_matching_media_infos(self, search_type, search_string,
                                 properties_list):
        """
        Queries for a list of information for tracks in the media library
        matching a specific field and value pair.
        """
        #self.logger.debug('get_matching_media_infos() not implemented.')
        #"""
        if search_type == 'Artist':
            match_query = xmmsclient.Match(artist=search_string)
        elif search_type == 'Title':
            match_query = xmmsclient.Match(title=search_string)
        elif search_type == 'Album':
            match_query = xmmsclient.Match(album=search_string)
        else:
            match_query = xmmsclient.Match()
            self.logger.debug('Cannot handle search_type: ' + search_type)

        self.sonus.coll_query_infos(match_query, properties_list,
                                    cb=self.infos_query_cb)
        #"""

    def ids_query_cb(self, xmms_result):
        """
        Callback for a collection query returning a list of IDs.
        """
        if not xmms_result.iserror():
            id_list = xmms_result.value()
        else:
            raise MlibResultError, xmms_result.get_error()

        # Emit a signal to inform the orignal caller of the query completion.
        self.emit(SIGNAL('got_all_media_ids(PyQt_PyObject)'), id_list)

    def infos_query_cb(self, xmms_result):
        """
        Callback for a collection query returning a list of track information.
        """
        if not xmms_result.iserror():
            mlib_info_list = xmms_result.value()
        else:
            raise MlibResultError, xmms_result.get_error()

        # Emit a signal to inform the orignal caller of the query completion.
        self.emit(SIGNAL('got_all_media_infos(PyQt_PyObject)'), mlib_info_list)


class MlibResultError:
    """
    Exception for a media library xmmsclient.XMMSResult error.
    """
    def __init__(self, error_detail):
        self.error_detail = error_detail

    def __repr__(self):
        return self.error_detail

    def log_error(self):
        self.logger.error(error_detail)
