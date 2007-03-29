"""
Provides an interface to XMMS2 media library functions.
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
from xmmsclient import collections as c


class Mlib(QObject):
    """
    The Mlib class is used to interface with the XMMS2 media library API from
    Sonus. It also contains miscellaneous related functions required for use
    by mlibgui.MlibWidget.
    """
    def __init__(self, sonus, parent=None):
        QObject.__init__(self, parent)
        self.sonus = sonus
        self.logger = logging.getLogger('Sonus.mlib')

    def getMediaInfo(self, entryId):
        """
        Queries for track information for a given media library entry id.
        """
        self.sonus.medialib_get_info(entryId, self._getMediaInfoCb)

    def getMediaInfoGui(self, xmmsResult): #FIXME
        """
        Queries for track information for a given media library entry id.
        This is dirty. FIXME!
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s', xmmsResult.get_error())
        else:
            self.sonus.medialib_get_info(xmmsResult.value(),
                                         self._getMediaInfoGuiCb)

    def _getMediaInfoCb(self, xmmsResult):
        """
        Callback for self.getMediaInfo.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s', xmmsResult.get_error())
        else:
            self.emit(SIGNAL('gotMediaInfo(PyQt_PyObject)'),
                             xmmsResult.value())

    def _getMediaInfoGuiCb(self, xmmsResult): #FIXME
        """
        Callback for self.getMediaInfo.
        This is dirty. FIXME!
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s', xmmsResult.get_error())
        else:
            self.emit(SIGNAL('gotMediaInfoGui(PyQt_PyObject)'),
                             xmmsResult.value())
