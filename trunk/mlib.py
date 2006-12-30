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
        Order up a list of all the track IDs in the media library.
        """
        self.sonus.coll_query_ids(self.all_media, cb=self.ids_query_cb)

    def get_all_media_infos(self, properties_list):
        """
        Order up a list of information for all tracks in the media library.
        """
        self.sonus.coll_query_infos(self.all_media, properties_list,
                                    cb=self.infos_query_cb)

    """
    This doesn't work. Python collections documentation sucks.
    """
    """
    def getColl(self, search_type, search_string):
        self.coll = xmmsclient.Match(self.all_media, field='artist', value='buckethead')
        self.matches = self.sonus.coll_query_infos(self.coll, ['title', 'duration', 'album'])
        print self.matches.value()
        for songs in self.matches:
            self.logger.debug("%(album)s - %(title)s (%(duration)s)" % song)
    """

    def ids_query_cb(self, xmms_result):
        """
        Callback for a collection query returning a list of IDs.
        """
        if not xmms_result.iserror():
            id_list = xmms_result.value()
        else:
            id_list = ['error']    #TODO: Raise exception?

        # Emit a signal to inform the orignal caller of the query completion.
        self.emit(SIGNAL('got_all_media_ids(PyQt_PyObject)'), id_list)

    def infos_query_cb(self, xmms_result):
        """
        Callback for a collection query returning a list of track information.
        """
        if not xmms_result.iserror():
            mlib_info_list = xmms_result.value()
        else:
            mlib_info_list = ['error']    #TODO: Raise exception?

        # Emit a signal to inform the orignal caller of the query completion.
        self.emit(SIGNAL('got_all_media_infos(PyQt_PyObject)'), mlib_info_list)
