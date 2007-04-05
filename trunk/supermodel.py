"""
The supermodel module houses the item model superclass.
For use with Sonus, a PyQt4 XMMS2 client.
"""

import operator
import logging

from PyQt4.QtCore import *

from collections import propertiesDict


class SuperModel(QAbstractTableModel):
    """
    The SuperModel class defines the standard interface that item models must
    use to be able to interoperate with other components in the model/view
    architecture. SuperModel is not supposed to be instantiated directly.
    Instead, you should subclass it to create new models.
    """
    def __init__(self, parent=None):
        """
        This constructor should be reimplemented in the subclass specifying
        a propertiesList and setting up signal connections for interacting with
        XMMS2. See mlibmodel.MlibModel.__init__ for an example.
        """
        QAbstractTableModel.__init__(self, parent)
        self.smLogger = logging.getLogger('Sonus.supermodel')

        """
        Our underlying data that the items in the model represent. It is a list
        of dictionaries. The dictionaries correspond to XMMS2 media information
        entries (eg. track information for a playlist or media library entry).
        """
        self.entryInfoList = []

        """
        The list of properties to return from XMMS2 queries.
        The order of the horizontal header sections reflects the order of the
        properties in this list.
        """
        self.propertiesList = ['id',]

        # When reimplementing, setup connections and initialize data, here.

    def initModelData(self, newEntryInfoList):
        """
        Initializes the data that the model provides.
        """
        self.replaceModelData(newEntryInfoList)
        self.emit(SIGNAL('modelInitialized()'))

        """
        We only initialize once, so here we disconnect the signal that
        triggered this function in the model subclass reimplementation. See
        mlibmodel.MlibModel.initModelData for an example.
        """

    def replaceModelData(self, newEntryInfoList=[]):
        """
        Replaces the current entryInfoList model data with a new one.
        """
        self.removeRows(0, self.rowCount()-1)
        self.insertRows(0, len(newEntryInfoList))
        self.entryInfoList = newEntryInfoList
        self.reset()

    def addOrUpdateEntry(self, entryInfo):
        """
        Adds data associated with an entry to the model. If the entry exists,
        it updates the entry data instead.
        """
        insertPosition = None
        if 'id' in self.propertiesList:
            # If the entry exists, use its list position as the insertPosition.
            for listItem in self.entryInfoList:
                try:
                    if entryInfo['id'] == listItem['id']:
                        insertPosition = self.entryInfoList.index(listItem)
                        break
                except KeyError, e:
                    self.smLogger.error(e)
                    break

        if insertPosition == None:
            insertPosition = self.rowCount()  # Insert after last row
            retVal = self.insertRows(insertPosition, count=1)
            if retVal == False:
                self.smLogger.error('Could not insert row into the model.')
                return

        for key in self.propertiesList:
            try:
                column = self.propertiesList.index(key)
            except ValueError, e:
                self.smLogger.error(e)
                continue
            index = self.createIndex(insertPosition, column)
            if index.isValid():
                try:
                    self.setData(index, entryInfo[key], Qt.DisplayRole)
                except KeyError, e:
                    self.setData(index, '', Qt.DisplayRole) # No info
            else:
                self.smLogger.error('Created index was invalid.')

        """
        On the first entry addition, data previously reported to views becomes
        invalid. Reset the model for any attached views.
        TODO: Might not need this check in later xmms2 versions. Try removing
        and testing in future versions.
        """
        if self.rowCount() == 1:
            self.reset()

    def rowCount(self, parent=QModelIndex()):
        """
        Returns the number of rows (entries) in the model.
        """
        return len(self.entryInfoList)

    def columnCount(self, parent=QModelIndex()):
        """
        Returns the number of columns (properties) in the model.
        If we cannot get the length of the first entry item, there are no
        columns. So, return a count of zero.
        """
        try:
            return len(self.entryInfoList[0])
        except IndexError, e:
            return 0

    def data(self, index, role):
        """
        Returns Qt.DisplayRole item data from the model at a particular index.
        """
        if not index.isValid():
            return QVariant()
        if role != Qt.DisplayRole:
            return QVariant()

        entry = index.row()
        try:
            property = self.propertiesList[index.column()]
            modelItem = self.entryInfoList[entry][property]
        except (TypeError, IndexError), e:
            self.smLogger.error(e)
            return QVariant()
        except KeyError, e:
            return QVariant()
        if modelItem is not None:
            return QVariant(modelItem)
        else:
            return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Returns the appropriate header title for a specified column (section).
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            try:
                key = self.propertiesList[section]
                return QVariant(propertiesDict[key])
            except (TypeError, IndexError, KeyError), e:
                self.smLogger.error(e)
                return QVariant()
        else:
            return QVariant()

    def sort(self, column, order=Qt.AscendingOrder):
        """
        Sorts the entries by 'column' (representing a media entry property) in
        the given order.
        """
        if not self.rowCount(): # If empty model
            return

        if order == Qt.AscendingOrder:
            isReversed = False
        else:
            isReversed = True

        try:
            propertyToSortOn = self.propertiesList[column]
        except (TypeError, IndexError), e:
            self.smLogger.error(e)
            return
        self.entryInfoList = sorted(self.entryInfoList,
                                    reverse=isReversed,
                                    key=operator.itemgetter(propertyToSortOn))

        self.reset()

    def setData(self, index, value, role):
        """
        Sets the 'role' data for the item at 'index' to 'value.'
        Returns true if successful; otherwise returns false.
        """
        if index.isValid() and role == Qt.DisplayRole:
            entry = index.row()
            try:
                property = self.propertiesList[index.column()]
                self.entryInfoList[entry][property] = value
            except (TypeError, IndexError, KeyError), e:
                self.smLogger.error(e)
                return False
            self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index,
                      index)
            return True
        else:
            self.smLogger.error('Invalid index or role supplied in setData.')
            return False

    def insertRows(self, position, count=1, parent=QModelIndex()):
        """
        Inserts 'count' rows into the model before the given row 'position.'
        The items in the new row will be children of the item represented by
        the parent model index, if the view specifies a parent.
        Returns true if the rows were successfully inserted; otherwise returns
        false.
        """
        # Manual range check since python's list.insert is too liberal.
        if (count < 0) or (position not in range(0, self.rowCount()+1)):
            return False

        self.beginInsertRows(QModelIndex(), position, position+count-1)

        for row in range(0, count):
            self.entryInfoList.insert(position, {})

        self.endInsertRows()
        return True

    def removeRows(self, position, count=1, parent=QModelIndex()):
        """
        Removes 'count' rows starting with the given 'row' under parent
        'parent' from the model.
        Returns true if the rows were successfully removed; otherwise returns
        false.
        """
        self.beginRemoveRows(QModelIndex(), position, position+count-1)

        for row in range(0, count):
            try:
                del self.entryInfoList[position]
            except IndexError, e:
                self.smLogger.error(e)
                return False

        self.endRemoveRows()
        return True

    def supportedDropActions(self):
        """
        Let the view know which actions are supported.
        """
        return Qt.MoveAction | Qt.CopyAction
    
    def flags(self, index):
        """
        Model tells the view which items can be dragged and dropped.
        """
        defaultFlags = QAbstractTableModel.flags(self, index)
        
        if index.isValid():
            return Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | defaultFlags
        else:
            return Qt.ItemIsDropEnabled | defaultFlags