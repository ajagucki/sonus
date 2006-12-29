"""
mlibgui: Sonus Mlib GUI
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from os import getenv
import logging

import mlibmodel


class MlibDialog(QDialog):
    def __init__(self, sonus, parent=None):
        QDialog.__init__(self, parent)

        self.logger = logging.getLogger('sonusLogger.mlibgui.MlibDialog')
        self.sonus = sonus

        self.setWindowTitle(self.tr("Media Library"))
        self.resize(QSize(640, 360))

        self.grid_layout = QGridLayout(self)

        self.frame = QFrame(self)

        self.frame_grid_layout = QGridLayout(self.frame)

        self.frame_hbox_layout = QHBoxLayout()

        self.label = QLabel(self.frame)
        self.label.setText(self.tr("&Search:"))
        self.frame_hbox_layout.addWidget(self.label)

        self.search_type_combo = QComboBox(self.frame)
        search_types = QStringList(["All", "Artist", "Title", "Album", "Raw"])
        self.search_type_combo.insertItems(0, search_types)
        self.frame_hbox_layout.addWidget(self.search_type_combo)

        self.search_line_edit = QLineEdit(self.frame)
        self.label.setBuddy(self.search_line_edit)
        self.frame_hbox_layout.addWidget(self.search_line_edit)
        self.frame_grid_layout.addLayout(self.frame_hbox_layout, 0, 0)

        self.model = mlibmodel.MlibModel(self.sonus, self.frame)

        self.table_view = QTableView(self.frame)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setShowGrid(False)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.verticalHeader().hide()
        #self.table_view.setSortingEnabled(True)
        self.frame_grid_layout.addWidget(self.table_view)
        self.grid_layout.addWidget(self.frame)

        self.hbox_layout = QHBoxLayout()

        spacer_item = QSpacerItem(131, 31, QSizePolicy.Expanding,
                                  QSizePolicy.Minimum)
        self.hbox_layout.addItem(spacer_item)

        self.refresh_button = QPushButton(self)
        self.refresh_button.setText(self.tr("Re&fresh"))
        self.refresh_button.setAutoDefault(False)
        self.hbox_layout.addWidget(self.refresh_button)

        self.add_button = QPushButton(self)
        self.add_button.setText(self.tr("&Add"))
        self.add_button.setAutoDefault(False)
        self.hbox_layout.addWidget(self.add_button)

        self.remove_button = QPushButton(self)
        self.remove_button.setText(self.tr("&Remove"))
        self.remove_button.setAutoDefault(False)
        self.hbox_layout.addWidget(self.remove_button)
        self.grid_layout.addLayout(self.hbox_layout, 1, 0)

        self.connect(self.refresh_button, SIGNAL('clicked()'), self.refresh)
        self.connect(self.add_button, SIGNAL('clicked()'), self.add_media)
        self.connect(self.remove_button, SIGNAL('clicked()'),
                     self.remove_media)
        """self.connect(self.search_line_edit, SIGNAL('returnPressed()'),
                     self.search)"""
        self.connect(self.model, SIGNAL('updated_model_data()'),
                     self.sync_model_view)

        self.setTabOrder(self.search_type_combo, self.search_line_edit)
        self.setTabOrder(self.search_line_edit, self.table_view)
        self.setTabOrder(self.table_view, self.add_button)
        self.setTabOrder(self.add_button, self.remove_button)

    def add_media(self):
        """
        Add media to the XMMS2 media library.
        """
        audio_files = QFileDialog.getOpenFileNames(
                        self, "Add Audio Files", getenv('HOME'),
                        "Audio (*.mp3 *.ogg *.flac)")
        # TODO: Attempt to add selected files to mlib

    def remove_media(self):
        """
        Remove media from the XMMS2 media library.
        """
        self.logger.debug('remove_media() called')

    def search(self):
        self.search_string = self.search_line_edit.text()
        self.search_type = self.search_type_combo.currentText()

        if str(self.search_string) == None:
            self.search_string = "*"

        if not self.search_type == "Raw":
            self.sonus.mlib.getColl(str(self.search_type),
                                    str(self.search_string))
        else:
            self.logger.info("Raw search not implemented yet.")

    def sync_model_view(self):
        """
        Synchronizes the view with the model's current data
        """
        self.table_view.setModel(self.model)
        self.table_view.hideColumn(self.model.columnCount()-1)
        self.table_view.resizeRowsToContents()
        self.table_view.resizeColumnsToContents()
        self.table_view.horizontalHeader().setStretchLastSection(True)

    def refresh(self):
        """
        Refresh the media library list
        """
        self.model.queryMlibRefresh()
