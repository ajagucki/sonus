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

        # Setup our connections
        self.connect(self.sonus.mlib,
                     SIGNAL('got_all_media_infos(PyQt_PyObject)'),
                     self.updateModelData)

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

        property = self.properties_list[index.column()]
        data_item = self.mlib_info_list[index.row()][property]
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

    def queryMlibRefresh(self):
        """
        Queries sonus.mlib for an update to the data the model provides.
        """
        self.sonus.mlib.get_all_media_infos(self.properties_list)

    def updateModelData(self, newer_mlib_info_list):
        """
        Updates the data that the model provides to a current copy from mlib.
        """
        if self.mlib_info_list != newer_mlib_info_list:
            self.mlib_info_list = newer_mlib_info_list
            self.emit(SIGNAL('dataChanged()'))
        else:
            self.logger.info('Media library is up to date. Not refreshing.')

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

        self.emit(SIGNAL('dataChanged()'))
