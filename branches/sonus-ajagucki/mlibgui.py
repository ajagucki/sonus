"""
Media library graphical user interface.
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from mlib import propertiesDict
import mlibmodel


class MlibDialog(QDialog):
    """
    The MlibDialog class defines the interface and functions of the media
    library. This dialog supports 'as-you-type' filtering to quickly and easily
    find entries in the library. Filtering by regular expression allows for
    powerful and complex patterns to be matched.
    """
    def __init__(self, sonus, parent=None):
        """
        MlibDialog's constructor creates all of its widgets, sets up their
        connections, and performs other initializations.
        """
        QDialog.__init__(self, parent)

        self.logger = logging.getLogger('Sonus.mlibgui')
        self.sonus = sonus

        self.setWindowTitle(self.tr('Sonus - Media Library'))
        self.resize(QSize(640, 360))

        self.sourceModel = mlibmodel.MlibModel(self.sonus, self)
        self.proxyModel = QSortFilterProxyModel(self)
        self.proxyModel.setDynamicSortFilter(True)

        self.gridLayout = QGridLayout(self)

        self.filterColumnComboBox = QComboBox(self)
        filterKeys = []
        for property in self.sourceModel.propertiesList:
            if not property == 'id':    # Remove after xmms2 bug #1339 is fixed
                filterKeys.append(propertiesDict[property])
        self.filterColumnComboBox.insertItems(0, QStringList(filterKeys))
        self.gridLayout.addWidget(self.filterColumnComboBox, 0, 0, 1, 1)

        self.filterPatternLineEdit = FilterPatternLineEdit(self)
        self.gridLayout.addWidget(self.filterPatternLineEdit, 0, 1, 1, 1)

        self.filterSyntaxComboBox = QComboBox(self)
        self.filterSyntaxComboBox.addItem(self.tr('RegExp'),
                                          QVariant(QRegExp.RegExp2))
        self.filterSyntaxComboBox.addItem(self.tr('Wildcard'),
                                          QVariant(QRegExp.Wildcard))
        self.filterSyntaxComboBox.addItem(self.tr('Exact'),
                                          QVariant(QRegExp.FixedString))
        self.gridLayout.addWidget(self.filterSyntaxComboBox, 0, 2, 1, 1)

        self.treeView = QTreeView(self)
        self.treeView.setRootIsDecorated(False)
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setSortingEnabled(True)
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

        self.connect(self.sourceModel, SIGNAL('modelInitialized()'),
                     self.initView)
        self.connect(self.filterPatternLineEdit,
                     SIGNAL('textChanged(const QString &)'),
                     self.filterRegExpChanged)
        self.connect(self.filterSyntaxComboBox,
                     SIGNAL('currentIndexChanged(int)'),
                     self.filterRegExpChanged)
        self.connect(self.filterColumnComboBox,
                     SIGNAL('currentIndexChanged(int)'),
                     self.filterColumnChanged)
        self.connect(self.treeView, SIGNAL('doubleClicked(QModelIndex)'),
                     self.addMediaToPlaylist)
        self.connect(self.addButton, SIGNAL('clicked()'), self.addMedia)
        self.connect(self.removeButton, SIGNAL('clicked()'),
                     self.removeMedia)

        self.setTabOrder(self.filterColumnComboBox, self.filterPatternLineEdit)
        self.setTabOrder(self.filterPatternLineEdit, self.filterSyntaxComboBox)
        self.setTabOrder(self.filterSyntaxComboBox, self.treeView)
        self.setTabOrder(self.treeView, self.addButton)
        self.setTabOrder(self.addButton, self.removeButton)

    def addMedia(self):
        """
        Adds media to the XMMS2 media library.
        """
        self.logger.debug('addMedia() not implemented.')
        """
        audioFiles = QFileDialog.getOpenFileNames(
                        self, 'Add Audio Files', os.getenv('HOME'),
                        'Audio (*.mp3 *.ogg *.flac)')
        # TODO: Attempt to add selected files to mlib
        """

    def removeMedia(self):
        """
        Removes media from the XMMS2 media library.
        """
        self.logger.debug('removeMedia() not implemented.')

    def initView(self):
        """
        Initializes the view, setting its model to a proxy model 'proxyModel'
        that provides sorting and filtering methods without changing the
        underlying data of the source model 'sourceModel.'
        """
        self.proxyModel.setSourceModel(self.sourceModel)
        self.filterColumnChanged()  # Remove after xmms2 bug #1339 is fixed
        self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.treeView.setModel(self.proxyModel)

    def filterRegExpChanged(self):
        """
        Filters the proxy model whenever the 'filterPatternLineEdit' has its
        text changed. The syntax used for the regular expression is determined
        by the current item in the 'filterSyntaxComboBox.' The key column to
        filter on is determined by the current item in the
        'filterColumnComboBox.'
        """
        if self.filterPatternLineEdit.hasDefautText:
            return
        syntax = \
            QRegExp.PatternSyntax(self.filterSyntaxComboBox.itemData(
                self.filterSyntaxComboBox.currentIndex()).toInt()[0])

        regExp = QRegExp(self.filterPatternLineEdit.text(), Qt.CaseInsensitive,
                         syntax)
        self.proxyModel.setFilterRegExp(regExp)

    def filterColumnChanged(self):
        """
        Changes the key column column to filter on whenever an item in the
        'filterColumnComboBox' is changed.
        """
        self.proxyModel.setFilterKeyColumn(
            self.filterColumnComboBox.currentIndex()+1) # +1 because bug #1339

    def addMediaToPlaylist(self, mediaIndex):
        """
        Adds selected media to the playlist.
        """
        if not mediaIndex.isValid():
            self.logger.error('Got invalid index.')
            return

        if 'id' in self.sourceModel.propertiesList:
            column = self.sourceModel.propertiesList.index('id')
        else:
            self.logger.error("The 'id' property is not in propertiesList.")
            return

        entryIdIndex = self.proxyModel.index(mediaIndex.row(), column)
        self.entryId = int(entryIdIndex.data(Qt.DisplayRole).toString())
        self.sonus.playlist.addTrack(self.entryId)

    def reject(self):
        """
        Effectively ignores calls to reject(), in case the user presses the
        escape key. The only reason this class is a QDialog is to allow
        detachment in the future.
        """
        pass


class FilterPatternLineEdit(QLineEdit):
    """
    Filter pattern line edit widget.
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
        self.setText('Filter entries...')
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
