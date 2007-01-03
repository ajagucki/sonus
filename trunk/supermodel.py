"""
XMMS2 Model superclass.
For use with Sonus, a PyQt4 XMMS2 client.
"""

import operator
import logging

from PyQt4.QtCore import *

from mlib import properties_dict


class SuperModel(QAbstractTableModel):
    """
    Abstract XMMS2 Model superclass to be subclassed by mlibmodel.MlibModel,
    playlistmodel.PlaylistModel, and any other XMMS2 related model.
    Warning: If you view the SuperModel directly, she may bitch at you.
    """
    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.logger = logging.getLogger('Sonus.supermodel')
        self.entry_info_list = []

        """
        The list of properties to return from XMMS2 queries.
        The order of the horizontal header sections reflects the order of the
        properties in this list.
        The 'id' property CANNOT be excluded due to either a bug or a feature
        in the XMMS2 python bindings, otherwise the View breaks. See bug
        report: http://bugs.xmms2.xmms.se/view.php?id=1339
        """
        self.properties_list = ['id',]
        if not 'id' in self.properties_list:
            err_msg = "The 'id' property is not in properties_list."
            self.logger.error(err_msg)
            raise err_msg

        """
        When reimplementing, setup connections and initialize data, here. See
        mlibmodel.MlibModel for an example.
        """

    def initModelData(self, new_entry_info_list):
        """
        Sets up the data that the model provides.
        """
        self.entry_info_list = new_entry_info_list
        self.emit(SIGNAL('model_initialized()'))

        # We only initialize once, so ignore future signals.
        """ removed """

    def replaceModelData(self, new_entry_info_list):
        """
        Replaces the current entry_info_list model data with a new one.
        """
        self.removeRows(0, self.rowCount()-1)
        self.insertRows(0, len(new_entry_info_list))
        self.entry_info_list = new_entry_info_list
        top_left = self.index(0, 0)
        bottom_right = self.index(self.rowCount()-1, self.columnCount()-1)
        self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'), top_left,
                         bottom_right)

    def addEntryToModel(self, info_entry):
        """
        Adds data associated with an entry to the model.
        """
        ins_position = 0
        ret_val = self.insertRows(ins_position, 1)
        if ret_val == False:
            self.logger.error('Could not insert rows into the model.')
            return

        for key in info_entry:
            try:
                column = self.properties_list.index(key[1])
            except ValueError:
                continue
            index = self.createIndex(ins_position, column)
            if index.isValid():
                try:
                    self.setData(index, info_entry[key], Qt.DisplayRole)
                except KeyError, e:
                    self.logger.error('%s, continuing.', e)
                    continue
            else:
                self.logger.error('Created index was invalid.')

    def rowCount(self, parent=QModelIndex()):
        """
        Return the number of rows (entries) in the tabel of model data.
        """
        return len(self.entry_info_list)

    def columnCount(self, parent=QModelIndex()):
        """
        Return the number of columns (properties) in the table of model data.
        """
        if self.rowCount() > 0:
            return len(self.entry_info_list[0])
        else:
            return 0

    def data(self, index, role):
        """
        Return data from the model at a particular index.
        """
        if not index.isValid():
            return QVariant()
        if role != Qt.DisplayRole:
            return QVariant()

        entry = index.row()
        try:
            property = self.properties_list[index.column()]
            data_item = self.entry_info_list[entry][property]
        except (TypeError, IndexError, KeyError), e:
            self.logger.error(e)
            return QVariant()
        if data_item is not None:
            return QVariant(data_item)
        else:
            return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Return the appropriate header title for a specified column (section).
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            try:
                key = self.properties_list[section]
                return QVariant(properties_dict[key])
            except (TypeError, IndexError, KeyError), e:
                self.logger.error(e)
                return QVariant()
        else:
            return QVariant()

    def sort(self, column, order=Qt.AscendingOrder):
        """
        Sorts the model by column in the given order.
        """
        if not len(self.entry_info_list):
            return

        if order == Qt.AscendingOrder:
            is_reversed = False
        else:
            is_reversed = True

        try:
            sort_property = self.properties_list[column]
        except (TypeError, IndexError), e:
            self.logger.error(e)
            return
        self.entry_info_list = sorted(self.entry_info_list,
                                      reverse=is_reversed,
                                      key=operator.itemgetter(sort_property))

        top_left = self.index(0, 0)
        bottom_right = self.index(self.rowCount()-1, self.columnCount()-1)
        self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'), top_left,
                         bottom_right)

    def setData(self, index, value, role):
        """
        Sets the 'role' data for the item at 'index' to 'value.'
        Returns true if successful; otherwise returns false.
        """
        if index.isValid() and role == Qt.DisplayRole:
            entry = index.row()
            try:
                property = self.properties_list[index.column()]
                self.entry_info_list[entry][property] = value
            except (TypeError, IndexError, KeyError), e:
                self.logger.error(e)
                return False
            self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index,
                      index)
            return True
        else:
            self.logger.error('Could not set data with given index and role.')
            return False

    def insertRows(self, position, count, parent=QModelIndex()):
        """
        Inserts 'count' rows into the model before the given row 'position.'
        The items in the new row will be children of the item represented by
        the parent model index, if the view specifies a parent.
        Returns true if the rows were successfully inserted; otherwise returns
        false.
        """
        self.beginInsertRows(QModelIndex(), position, position+count-1)

        for row in range(0, count):
            self.entry_info_list.insert(position, {})

        self.endInsertRows()
        return True

    def removeRows(self, position, count, parent=QModelIndex()):
        """
        Removes 'count' rows starting with the given 'row' under parent
        'parent' from the model.
        Returns true if the rows were successfully removed; otherwise returns
        false.
        """
        self.beginRemoveRows(QModelIndex(), position, position+count-1)

        for row in range(0, count):
            del self.entry_info_list[position]

        self.endRemoveRows()
        return True
