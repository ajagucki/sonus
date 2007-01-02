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
        self.setSizeGripEnabled(True)

        self.model = mlibmodel.MlibModel(self.sonus, self)

        self.grid_layout = QGridLayout(self)

        self.label = QLabel(self)
        self.label.setText(self.tr('&Search:'))
        self.grid_layout.addWidget(self.label, 0, 0, 1, 1)

        self.search_type_combo = QComboBox(self)
        search_types = QStringList(['All', 'Artist', 'Title', 'Album', 'Raw'])
        self.search_type_combo.insertItems(0, search_types)
        self.grid_layout.addWidget(self.search_type_combo, 0, 1, 1, 1)

        self.search_line_edit = QLineEdit(self)
        self.grid_layout.addWidget(self.search_line_edit, 0, 2, 1, 1)

        self.table_view = QTableView(self)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setShowGrid(False)
        self.table_view.setTabKeyNavigation(False)
        self.table_view.setSortingEnabled(True)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.verticalHeader().hide()
        self.grid_layout.addWidget(self.table_view, 1, 0, 1, 3)

        self.refresh_button = QPushButton(self)
        self.refresh_button.setText(self.tr('Re&fresh'))
        self.refresh_button.setAutoDefault(False)

        self.add_button = QPushButton(self)
        self.add_button.setText(self.tr('&Add'))
        self.add_button.setAutoDefault(False)

        self.remove_button = QPushButton(self)
        self.remove_button.setText(self.tr('&Remove'))
        self.remove_button.setAutoDefault(False)

        self.button_box = QDialogButtonBox(self)
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.addButton(self.refresh_button,
            QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.add_button, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.remove_button,
            QDialogButtonBox.ActionRole)
        self.grid_layout.addWidget(self.button_box, 2, 2, 1, 1)
        self.label.setBuddy(self.search_line_edit)

        self.connect(self.refresh_button, SIGNAL('clicked()'),
                     self.refresh_model)
        self.connect(self.add_button, SIGNAL('clicked()'), self.add_media)
        self.connect(self.remove_button, SIGNAL('clicked()'),
                     self.remove_media)
        self.connect(self.search_line_edit, SIGNAL('returnPressed()'),
                     self.search)
        self.connect(self.model, SIGNAL('dataChanged()'),
                     self.sync_model_view)
        self.connect(self.table_view, SIGNAL('doubleClicked(QModelIndex)'),
                     self.add_media_to_playlist)

        self.setTabOrder(self.search_type_combo, self.search_line_edit)
        self.setTabOrder(self.search_line_edit, self.table_view)
        self.setTabOrder(self.table_view, self.refresh_button)
        self.setTabOrder(self.refresh_button, self.add_button)
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
        self.logger.debug('search() not implemented.')
        """
        search_string = str(self.search_line_edit.text())
        search_type = self.search_type_combo.currentText()

        if search_string == None:
            search_string = '*'

        if search_type != 'Raw':
            self.sonus.mlib.get_matching_media_infos(
                search_type,
                search_string,
                self.model.properties_list)
        else:
            self.logger.info('Raw search not implemented yet.')
        """

    def sync_model_view(self):
        """
        Synchronizes the view with the model's current data.
        """
        self.table_view.setModel(self.model)
        #self.table_view.resizeRowsToContents()      # These take a LONG TIME,
        #self.table_view.resizeColumnsToContents()   # commenting out for now
        self.table_view.horizontalHeader().setStretchLastSection(True)

    def refresh_model(self):
        """
        Refresh the media library list
        """
        self.model.queryMlibRefresh()

    def add_media_to_playlist(self):
        """
        Adds selected media to the playlist.
        """
        self.logger.debug("Got double click")
