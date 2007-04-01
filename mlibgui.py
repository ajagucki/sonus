"""
Media library graphical user interface.
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import mlibmodel


class MlibWidget(QWidget):
    """
    The MlibWidget class defines the interface and functions of the media
    library.
    """
    def __init__(self, sonus, parent=None):
        """
        MlibWidget's constructor creates all of its widgets, sets up their
        connections, and performs other initializations.
        """
        QWidget.__init__(self, parent)

        self.logger = logging.getLogger('Sonus.mlibgui')
        self.sonus = sonus

        self.setWindowTitle(self.tr('Sonus - Media Library'))
        self.resize(QSize(640, 360))

        self.model = mlibmodel.MlibModel(self.sonus, self)

        self.gridLayout = QGridLayout(self)

        self.searchTypeComboBox = QComboBox(self)
        searchTypes = QStringList(['All', 'Artist', 'Title', 'Album'])
        self.searchTypeComboBox.insertItems(0, searchTypes)
        self.gridLayout.addWidget(self.searchTypeComboBox, 0, 0, 1, 1)
        self.lastSearchString = ''

        self.searchLineEdit = SearchLineEdit(self)
        self.gridLayout.addWidget(self.searchLineEdit, 0, 1, 1, 1)

        self.checkBox = QCheckBox(self)
        self.checkBox.setText(self.tr('&Exact'))
        self.gridLayout.addWidget(self.checkBox, 0, 2, 1, 1)

        self.treeView = QTreeView(self)
        self.treeView.setRootIsDecorated(False)
        self.treeView.setItemsExpandable(False)
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setSortingEnabled(True)
        self.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.gridLayout.addWidget(self.treeView, 1, 0, 1, 3)

        self.addButton = QPushButton(self)
        self.addButton.setText(self.tr('&Add'))
        self.addButton.setAutoDefault(False)

        self.removeButton = QPushButton(self)
        self.removeButton.setText(self.tr('&Remove'))
        self.removeButton.setAutoDefault(False)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.addButton(self.addButton, QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.removeButton,
                                 QDialogButtonBox.ActionRole)
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 3)

        self.connect(self.addButton, SIGNAL('clicked()'), self.addMedia)
        self.connect(self.removeButton, SIGNAL('clicked()'), self.removeMedia)
        self.connect(self.searchLineEdit, SIGNAL('returnPressed()'),
                     self.search)
        self.connect(self.searchTypeComboBox,
                     SIGNAL('currentIndexChanged(int)'), self.search)
        self.connect(self.checkBox, SIGNAL('stateChanged(int)'), self.search)
        self.connect(self.model, SIGNAL('modelInitialized()'), self.initView)
        self.connect(self.treeView, SIGNAL('doubleClicked(QModelIndex)'),
                     self.addMediaToPlaylist)

        self.setTabOrder(self.searchTypeComboBox, self.searchLineEdit)
        self.setTabOrder(self.searchLineEdit, self.checkBox)
        self.setTabOrder(self.checkBox, self.addButton)
        self.setTabOrder(self.addButton, self.removeButton)

    def addMedia(self):
        """
        Adds media to the XMMS2 media library.
        """
        audioFileNames = QFileDialog.getOpenFileNames(
                        self,
                        'Add Audio Files',
                        os.getenv('HOME'),
                        'Audio Files (*.mp3 *.ogg *.flac)') # TODO: all formats

        # str(fileName) converts from QString to Python string
        for fileName in audioFileNames:
            self.sonus.medialib_add_entry('file://' + str(fileName),
                                          self._addMediaCb)
        """
        FIXME: Force a refresh. Metadata may not be hashed in time here.
        TODO: Need support for mlib "entry added/changed" broadcasts instead.
        Remove the last 2 lines of this function once fixed.
        """
        self.searchLineEdit.setText('')
        self.search()

    def _addMediaCb(self, xmmsResult):
        """
        Callback for mlibgui.addMedia.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s', xmmsResult.get_error())
        else:
            pass    # xmmsResult.value() is None, no problem.

    def removeMedia(self):
        """
        Removes selected media from the XMMS2 media library.
        """
        selectionModel = self.treeView.selectionModel()
        indexes = selectionModel.selectedIndexes()

        if 'id' in self.model.propertiesList:
            column = self.model.propertiesList.index('id')
        else:
            self.logger.error("The 'id' property is not in propertiesList.")
            return

        for index in indexes:
            if index.column() != column:
                break
            entryId = int(index.data(Qt.DisplayRole).toString())
            self.logger.info('Removing entry %s from the media library.',
                              entryId)
            self.sonus.medialib_remove_entry(entryId, self._removeMediaCb)

        """
        FIXME: Force a refresh.
        TODO: Need support for mlib "removed" broadcast instead.
        Remove the last 2 lines of this function once fixed.
        """
        self.searchLineEdit.setText('')
        self.search()

    def _removeMediaCb(self, xmmsResult):
        """
        Callback for mlibgui.removeMedia.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s', xmmsResult.get_error())
        else:
            pass    # xmmsResult.value() is None, no problem.

    def search(self):
        """
        Performs a search query on the media library.
        """
        searchString = str(self.searchLineEdit.text())
        searchType = self.searchTypeComboBox.currentText()

        if searchString == '':
            searchString = '%'  # Wildcard
        else:
            if self.checkBox.checkState() == Qt.Unchecked:
                searchString = searchString.replace('*', '%')
                searchString = '%%%s%%' % searchString  # Wrap in wildcards

        self.sonus.collections.searchCollInfos(searchType, searchString,
                                               self.model.propertiesList)

    def initView(self):
        """
        Initializes the view, setting its model.
        """
        self.treeView.setModel(self.model)

    def addMediaToPlaylist(self, mediaIndex):
        """
        Adds selected media to the playlist.
        """
        if not mediaIndex.isValid():
            self.logger.error('Got invalid index.')
            return

        if 'id' in self.model.propertiesList:
            column = self.model.propertiesList.index('id')
        else:
            self.logger.error("The 'id' property is not in propertiesList.")
            return

        entryIdIndex = self.model.index(mediaIndex.row(), column)
        self.entryId = int(entryIdIndex.data(Qt.DisplayRole).toString())
        self.sonus.playlist.addTrack(self.entryId)


class SearchLineEdit(QLineEdit):
    """
    Search line edit widget.
    """
    def __init__(self, parent=None):
        """
        Constructor that initializes the instruction text to a light grey.
        """
        QLineEdit.__init__(self, parent)
        palette = self.palette()
        self.oldTextColor = palette.color(QPalette.Text)
        palette.setColor(QPalette.Text, QColor('#777777'))
        self.setPalette(palette)
        self.setText('Enter search terms...')
        self.hasDefautText = True

    def focusInEvent(self, event=None):
        """
        On the first 'focus in' event, clears the line edit and resets its
        text color to its normal value.
        """
        if self.hasDefautText:
            palette = self.palette()
            palette.setColor(QPalette.Text, self.oldTextColor)
            self.setPalette(palette)
            self.clear()
            self.hasDefautText = False
        QLineEdit.focusInEvent(self, event)
