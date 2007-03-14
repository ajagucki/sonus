"""
Provides an interface to XMMS2 collections functions.
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
from xmmsclient import collections as c


class Collections(QObject):
    """
    The Collections class is used to interface with the XMMS2 collections
    API from Sonus.
    """
    def __init__(self, sonus, parent=None):
        QObject.__init__(self, parent)
        self.sonus = sonus
        self.logger = logging.getLogger('Sonus.collections')

    def getAllCollInfos(self, propertiesList):
        """
        Queries for a list of information for all tracks in Universe.
        """
        self.sonus.coll_query_infos(c.Universe(), propertiesList,
                                    cb=self._getAllCollInfosCb)

    def getCollInfoPlaylist(self, entryIdList, propertiesList):
        """
        Queries for track information for a given media library entry id.
        Playlist specific.
        """
        self.propertiesList = propertiesList[:]
        if 'id' not in propertiesList:
            propertiesList.append('id')

        collIDList  = c.IDList()
        self.entryIdList = entryIdList
        for entryId in self.entryIdList:
            collIDList.ids.append(entryId)

        self.sonus.coll_query_infos(collIDList, propertiesList,
                                    cb=self._getCollInfosPlaylistCb)

    def searchCollInfos(self, searchType, searchString, propertiesList):
        """
        Queries for a list of information for tracks in the media library
        matching a specific field and value pair.
        """ 
        if searchType == 'All':
            collection  = c.Universe()
            collection &= c.Match(field='id', value='')  # Null set
            for property in propertiesList:
                collection |= c.Match(field=property,
                                                  value=searchString)
        else:
            for key, value in propertiesDict.items():
                if searchType == value:
                    collection = c.Match(field=key,
                                                     value=searchString)
                    break
            else:
                self.logger.error('Cannot handle search type: %s', searchType)
                return

        self.logger.info("Searching media library under '%s' for '%s'",
                         searchType, searchString)
        self.sonus.coll_query_infos(collection, propertiesList,
                                    cb=self._searchCollInfosCb)

    def _getAllCollInfosCb(self, xmmsResult):
        """
        Callback for self.getAllMediaInfos.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s', xmmsResult.get_error())
        else:
            entryInfoList = xmmsResult.value()
            self.emit(SIGNAL('gotAllCollInfos(PyQt_PyObject)'),
                             entryInfoList)

    def _getCollInfosPlaylistCb(self, xmmsResult):
        """
        Callback for self.searchedMediaInfosPlaylist.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s', xmmsResult.get_error())
        else:
            entryInfoList = xmmsResult.value()
            sortedEntryInfoList = []

            # Create a dict with proper playlist order
            for entryId in self.entryIdList:
                for dict in entryInfoList:
                    if dict['id'] == entryId:
                        tempDict = dict.copy()
                        if 'id' not in self.propertiesList:
                            del tempDict['id']
                        sortedEntryInfoList.append(tempDict)
                        break

            self.emit(SIGNAL('gotCollInfosPlaylist(PyQt_PyObject)'),
                             sortedEntryInfoList)
    
    def _searchCollInfosCb(self, xmmsResult):
        """
        Callback for self.searchMediaInfos.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s', xmmsResult.get_error())
        else:
            entryInfoList = xmmsResult.value()
            self.emit(SIGNAL('searchedCollInfos(PyQt_PyObject)'),
                             entryInfoList)