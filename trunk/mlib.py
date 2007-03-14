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
    by mlibgui.MlibDialog.
    """
    def __init__(self, sonus, parent=None):
        QObject.__init__(self, parent)
        self.sonus = sonus
        self.logger = logging.getLogger('Sonus.mlib')

        """
        Set a callback to handle an 'entry changed' broadcast.
        Note: We don't monitor an 'entry added' broadcast since the metadata
        for the added entry may not be up to date until the correct
        'entry changed' broadcast is sent. Also, when paths are added, we do
        not receive 'entry added' broadcasts, only 'entry changed' broadcasts.
        """
        self.sonus.broadcast_medialib_entry_changed(self._entryChangedCb)

    def getMediaInfo(self, entryId):
        """
        Queries for track information for a given media library entry id.
        """
        self.sonus.medialib_get_info(entryId, self._getMediaInfoCb)

    def _getMediaInfoCb(self, xmmsResult):
        """
        Callback for self.getMediaInfo.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s', xmmsResult.get_error())
        else:
            entryInfo = xmmsResult.value()
            self.emit(SIGNAL('gotMediaInfo(PyQt_PyObject)'), entryInfo)

    def _entryChangedCb(self, xmmsResult):
        """
        Callback for the media library 'entry changed' broadcast.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s', xmmsResult.get_error())
        else:
            entryId = xmmsResult.value()
            self.logger.info('Entry %s changed in media library.', entryId)
            self.emit(SIGNAL('entryChanged()'))
            self.getMediaInfo(entryId)


"""
An incomplete dictionary of properties as defined in the XMMS2 source
code: src/include/xmms/xmms_medialib.h
"""
propertiesDict = {
    'title':'Title',
    'artist':'Artist',
    'album':'Album',
    'tracknr':'Track',
    'duration':'Length',
    'id':'ID',
}
