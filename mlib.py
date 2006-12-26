"""
mlib: Basic xmms2 medialib functions
For use with Sonus, a PyQt4 XMMS2 client.
"""

from PyQt4 import QtCore
import xmmsclient

import logging


class Mlib(QtCore.QObject):
    def __init__(self, sonus, parent=None):
        self.sonus = sonus
        self.logger = logging.getLogger('sonusLogger.mlib.Mlib')
        self.allmedia = xmmsclient.Universe()
        QtCore.QObject.__init__(self, parent)
        self.idList = []

    def get_all_media(self):
        """
        Order up a list of all the tracks in the media library
        """
        self.sonus.coll_query_ids(self.allmedia, cb=self.callback)
    
    """
    This doesn't work. Python collections documentation sucks.
    """
    def getColl(self, search_type, search_string):
        self.coll = xmmsclient.Match(self.allmedia, field='artist', value='buckethead')
        self.matches = self.sonus.coll_query_infos(self.coll, ['title', 'duration', 'album'])
        print self.matches.value()
        for songs in self.matches:
            self.logger.debug("%(album)s - %(title)s (%(duration)s)" % song)

    def callback(self, result):
        """
        Callback for the collection query
        """
        if not result.iserror():
            self.idList = result.value()
        else:
            self.idList = ['error']    #TODO: Raise exception?

        """
        Now we want to try and emit a signal to inform the gui
        """
        self.emit(QtCore.SIGNAL('got_all_media(PyQt_PyObject)'), self.idList)
