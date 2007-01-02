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
        self.search_line_edit.setFocus()
        self.grid_layout.addWidget(self.search_line_edit, 0, 2, 1, 1)

        self.table_view = QTableView(self)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setShowGrid(False)
        self.table_view.setTabKeyNavigation(False)
        self.table_view.setSortingEnabled(True)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
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
        self.grid_layout.addWidget(self.button_box, 2, 2, 1, 1)
        self.label.setBuddy(self.search_line_edit)

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
        self.setTabOrder(self.search_line_edit, self.table_view)
        self.setTabOrder(self.table_view, self.add_button)
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
        search_string = str(self.search_line_edit.text())
        search_type = self.search_type_combo.currentText()

        if search_string == '':
            search_string = '%'
        else:
            search_string = search_string.replace('*', '%')
            search_string = '%%%s%%' % search_string

        self.sonus.mlib.search_media_infos(search_type, search_string,
                                           self.model.properties_list)

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

        if 'id' in self.model.properties_list:
            column = self.model.properties_list.index('id')
        else:
            self.logger.error("The 'id' property is not in properties_list.")
            return

        track_id_index = self.model.index(media_index.row(), column)
        self.track_id = track_id_index.data(Qt.DisplayRole).toString()
        self.logger.debug('Double click: %s', self.track_id)
        # self.sonus.playlist.add_track(track_id)
