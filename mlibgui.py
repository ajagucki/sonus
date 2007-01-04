"""
mlibgui: Media library dialog
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import mlibmodel


class MlibDialog(QDialog):
    def __init__(self, sonus, parent=None):
        QDialog.__init__(self, parent)

        self.logger = logging.getLogger('Sonus.mlibgui')
        self.sonus = sonus

        self.setWindowTitle(self.tr('Sonus - Media Library'))
        self.resize(QSize(640, 360))

        self.model = mlibmodel.MlibModel(self.sonus, self)

        self.grid_layout = QGridLayout(self)

        self.search_type_combo = QComboBox(self)
        search_types = QStringList(['All', 'Artist', 'Title', 'Album'])
        self.search_type_combo.insertItems(0, search_types)
        self.grid_layout.addWidget(self.search_type_combo, 0, 0, 1, 1)

        self.search_line_edit = SearchLineEdit(self)
        self.grid_layout.addWidget(self.search_line_edit, 0, 1, 1, 1)

        self.check_box = QCheckBox(self)
        self.check_box.setText(self.tr('&Exact'))
        self.grid_layout.addWidget(self.check_box, 0, 2, 1, 1)

        self.table_view = QTableView(self)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setShowGrid(False)
        self.table_view.setTabKeyNavigation(False)
        self.table_view.setFocusPolicy(Qt.NoFocus)
        self.table_view.setSortingEnabled(True)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.verticalHeader().setDefaultSectionSize(20)
        self.table_view.verticalHeader().setResizeMode(QHeaderView.Fixed)
        self.table_view.verticalHeader().hide()
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.grid_layout.addWidget(self.table_view, 1, 0, 1, 3)

        self.add_button = QPushButton(self)
        self.add_button.setText(self.tr('&Add'))
        self.add_button.setAutoDefault(False)

        self.remove_button = QPushButton(self)
        self.remove_button.setText(self.tr('&Remove'))
        self.remove_button.setAutoDefault(False)

        self.button_box = QDialogButtonBox(self)
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.addButton(self.add_button, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.remove_button,
            QDialogButtonBox.ActionRole)
        self.grid_layout.addWidget(self.button_box, 2, 0, 1, 3)

        self.connect(self.add_button, SIGNAL('clicked()'), self.add_media)
        self.connect(self.remove_button, SIGNAL('clicked()'),
                     self.remove_media)
        self.connect(self.search_line_edit, SIGNAL('returnPressed()'),
                     self.search)
        self.connect(self.model, SIGNAL('model_initialized()'),
                     self.init_view)
        self.connect(self.table_view, SIGNAL('doubleClicked(QModelIndex)'),
                     self.add_media_to_playlist)

        self.setTabOrder(self.search_type_combo, self.search_line_edit)
        self.setTabOrder(self.search_line_edit, self.check_box)
        self.setTabOrder(self.check_box, self.add_button)
        self.setTabOrder(self.add_button, self.remove_button)

    def add_media(self):
        """
        Add media to the XMMS2 media library.
        """
        self.logger.debug('add_media() not implemented.')
        """
        audio_files = QFileDialog.getOpenFileNames(
                        self, 'Add Audio Files', os.getenv('HOME'),
                        'Audio (*.mp3 *.ogg *.flac)')
        # TODO: Attempt to add selected files to mlib
        """

    def remove_media(self):
        """
        Remove media from the XMMS2 media library.
        """
        self.logger.debug('remove_media() not implemented.')

    def search(self):
        """
        Performs a search query on the media library.
        """
        search_string = str(self.search_line_edit.text())
        search_type = self.search_type_combo.currentText()

        if search_string == '':
            search_string = '%'
        else:
            if self.check_box.checkState() == Qt.Unchecked:
                search_string = search_string.replace('*', '%')
                search_string = '%%%s%%' % search_string

        self.sonus.mlib.search_media_infos(search_type, search_string,
                                           self.model.propertiesList)

    def init_view(self):
        """
        Initializes the view, setting its model.
        """
        self.table_view.setModel(self.model)

    def add_media_to_playlist(self, media_index):
        """
        Adds selected media to the playlist.
        """
        if not media_index.isValid():
            self.logger.error('Got invalid index.')
            return

        if 'id' in self.model.propertiesList:
            column = self.model.propertiesList.index('id')
        else:
            self.logger.error("The 'id' property is not in propertiesList.")
            return

        track_id_index = self.model.index(media_index.row(), column)
        self.track_id = int(track_id_index.data(Qt.DisplayRole).toString())
        self.sonus.playlist.add_track(self.track_id)

    def reject(self):
        """
        Effectively ignores calls to reject(), in case the user presses the
        escape key. The only reason this class is a QDialog is to allow
        detachment in the future.
        """
        pass


class SearchLineEdit(QLineEdit):
    """
    Search line edit widget.
    """
    def __init__(self, parent=None):
        """
        Constructor that initializes the instruction text to grey and.
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
        Clears and resets to a normal text color on a 'focus in' event.
        """
        if self.hasDefautText:
            palette = self.palette()
            palette.setColor(QPalette.Text, self.oldTextColor)
            self.setPalette(palette)
            self.clear()
            self.hasDefautText = False
        QLineEdit.focusInEvent(self, event)
