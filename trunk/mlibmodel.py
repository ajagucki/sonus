"""
mlibmodel: Media library model for mlibgui.MlibDialog's QTableView
For use with Sonus, a PyQt4 XMMS2 client.
"""

import operator
import logging

from PyQt4.QtCore import *


class MlibModel(QAbstractTableModel):
    def __init__(self, sonus, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.sonus = sonus
        self.logger = logging.getLogger('Sonus.mlibmodel')
        self.mlib_info_list = []

        """
        The list of properties to return from mlib.
        The order of the horizontal header sections reflects the order of the
        properties in this list.
        The 'id' property CANNOT be excluded due to either a bug or a feature
        in the XMMS2 python bindings, otherwise the View breaks. See bug
        report: http://bugs.xmms2.xmms.se/view.php?id=1339
        """
        self.properties_list = ['id', 'artist', 'title', 'album']
        if not 'id' in self.properties_list:
            err_msg = "The 'id' property is not in properties_list."
            self.logger.error(err_msg)
            raise err_msg

        # Setup our connections
        self.connect(self.sonus.mlib,
                     SIGNAL('got_all_media_infos(PyQt_PyObject)'),
                     self.initModelData)
        self.connect(self.sonus.mlib, SIGNAL('got_media_info(PyQt_PyObject)'),
                     self.addMlibEntryToModel)
        self.connect(self.sonus.mlib,
                     SIGNAL('searched_media_infos(PyQt_PyObject)'),
                     self.replaceModelData)

        # Initiaize our data
        self.sonus.mlib.get_all_media_infos(self.properties_list)

    def initModelData(self, new_mlib_info_list):
        """
        Sets up the data that the model provides to a current copy from mlib.
        """
        self.mlib_info_list = new_mlib_info_list
        self.emit(SIGNAL('model_initialized()'))

        # We only initialize once, so ignore future signals.
        self.disconnect(self.sonus.mlib,
                        SIGNAL('got_all_media_infos(PyQt_PyObject)'),
                        self.initModelData)

    def replaceModelData(self, new_mlib_info_list):
        """
        Replaces the current mlib_info_list model data with a new one.
        """
        self.logger.debug('Replacing model data with: %s', new_mlib_info_list)
        self.removeRows(0, self.rowCount()-1)
        self.insertRows(0, len(new_mlib_info_list))
        self.mlib_info_list = new_mlib_info_list
        top_left = self.index(0, 0)
        bottom_right = self.index(self.rowCount()-1, self.columnCount()-1)
        self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'), top_left,
                         bottom_right)

    def addMlibEntryToModel(self, mlib_info_entry):
        """
        Adds data associated with a media library entry to the model.
        """
        ins_position = 0
        ret_val = self.insertRows(ins_position, 1)
        if ret_val == False:
            self.logger.error('Could not insert rows into the model.')
            return

        for key in mlib_info_entry:
            try:
                column = self.properties_list.index(key[1])
            except ValueError:
                continue
            index = self.createIndex(ins_position, column)
            if index.isValid():
                self.setData(index, mlib_info_entry[key], Qt.DisplayRole)
            else:
                self.logger.error('Created index was invalid.')

    def rowCount(self, parent=QModelIndex()):
        """
        Return the number of tracks in the media library.
        """
        return len(self.mlib_info_list)

    def columnCount(self, parent=QModelIndex()):
        """
        Number of columns, essentially number of different metadata
        types we want to make viewable. (eg. title, artist, album, etc.)
        """
        if self.rowCount() > 0:
            return len(self.mlib_info_list[0])
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

        mlib_entry = index.row()
        property = self.properties_list[index.column()]
        data_item = self.mlib_info_list[mlib_entry][property]
        if data_item is not None:
            return QVariant(data_item)
        else:
            return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Return the appropriate header title for a specified column (section).
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            key = self.properties_list[section]
            return QVariant(self.sonus.mlib.properties_dict[key])
        else:
            return QVariant()

    def sort(self, column, order=Qt.AscendingOrder):
        """
        Sorts the model by column in the given order.
        """
        if not len(self.mlib_info_list):
            return

        if order == Qt.AscendingOrder:
            is_reversed = False
        else:
            is_reversed = True

        sort_property = self.properties_list[column]
        self.mlib_info_list = sorted(self.mlib_info_list, reverse=is_reversed,
            key=operator.itemgetter(sort_property))

        top_left = self.index(0, 0)
        bottom_right = self.index(self.rowCount()-1, self.columnCount()-1)
        self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'), top_left,
                         bottom_right)

    """def flags(self, index):
        ""
        Returns the item flags for the given index, which is required to make
        this model editable.
        The base class implementation returns a combination of flags that
        enables the item (ItemIsEnabled) and allows it to be selected
        (ItemIsSelectable).
        ""
        if not index.isValid():
            return Qt.ItemIsEnabled

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable"""

    def setData(self, index, value, role):
        """
        Sets the 'role' data for the item at 'index' to 'value.'
        Returns true if successful; otherwise returns false.
        """
        if index.isValid() and role == Qt.DisplayRole:
            mlib_entry = index.row()
            property = self.properties_list[index.column()]
            self.mlib_info_list[mlib_entry][property] = value
            self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index,
                      index)
            self.logger.debug('Set data: %s, %s', index.row(), index.column())
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
            self.mlib_info_list.insert(position, {})

        self.endInsertRows()
        self.logger.debug('Inserted %d row(s) before row %d.', count, position)
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
            del self.mlib_info_list[position]

        self.endRemoveRows()
        return True
