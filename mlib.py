"""
mlib: Basic xmms2 medialib functions
For use with Sonus, a PyQt4 XMMS2 client.
"""

from PyQt4 import QtCore
from xmmsclient import Universe

import logging


class Mlib(QtCore.QObject):
    def __init__(self, sonus, parent=None):
        self.sonus = sonus
        self.logger = logging.getLogger('sonusLogger.mlib.Mlib')
        QtCore.QObject.__init__(self, parent)
        self.idList = []

    def get_all_media(self):
        """
        Order up a list of all the tracks in the media library
        """
        allmedia = Universe()
        self.logger.debug("From getAllMedia(): %s" % allmedia)   #DEBUG
        self.sonus.coll_query_ids(allmedia, cb=self.callback)

    def callback(self, result):
        """
        Callback for the collection query
        """
        self.logger.debug("From callback(): %s" % result)    #DEBUG
        if not result.iserror():
            self.idList = result.value()
        else:
            self.idList = ['error']    #TODO: Raise exception?

        """
        Now we want to try and emit a signal to inform the gui
        """
        self.logger.debug("mlibmodel: Emitting singal 'got_all_media()'")    #DEBUG
        self.emit(QtCore.SIGNAL('got_all_media()'))
