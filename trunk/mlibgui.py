"""
mlibgui: Sonus Mlib GUI
"""
from PyQt4 import QtCore, QtGui

class MlibDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.grid_layout = QtGui.QGridLayout(self)

        self.frame = QtGui.QFrame(self)

        self.frame_grid_layout = QtGui.QGridLayout(self.frame)

        self.frame_hbox_layout = QtGui.QHBoxLayout()

        self.label = QtGui.QLabel(self.frame)
        self.frame_hbox_layout.addWidget(self.label)

        self.search_type_combo = QtGui.QComboBox(self.frame)
        self.frame_hbox_layout.addWidget(self.search_type_combo)

        self.search_line_edit = QtGui.QLineEdit(self.frame)
        self.frame_hbox_layout.addWidget(self.search_line_edit)
        self.frame_grid_layout.addLayout(self.frame_hbox_layout, 0, 0)

        self.list_view = QtGui.QListView(self.frame)
        self.frame_grid_layout.addWidget(self.list_view)
        self.grid_layout.addWidget(self.frame)

        self.hbox_layout = QtGui.QHBoxLayout()

        spacer_item = QtGui.QSpacerItem(131, 31, QtGui.QSizePolicy.Expanding,
                                        QtGui.QSizePolicy.Minimum)
        self.hbox_layout.addItem(spacer_item)

        self.add_button = QtGui.QPushButton(self)
        self.add_button.setAutoDefault(False)
        self.hbox_layout.addWidget(self.add_button)

        self.remove_button = QtGui.QPushButton(self)
        self.remove_button.setAutoDefault(False)
        self.hbox_layout.addWidget(self.remove_button)
        self.grid_layout.addLayout(self.hbox_layout, 1, 0)
        self.label.setBuddy(self.search_line_edit)

        self.setWindowTitle(self.tr("Media Library"))
        self.resize(QtCore.QSize(650, 300))
        self.label.setText(self.tr("&Search:"))
        self.add_button.setText(self.tr("&Add"))
        self.remove_button.setText(self.tr("&Remove"))

        search_types = QtCore.QStringList(["All", "Artist", "Title", "Album"])
        self.search_type_combo.insertItems(0, search_types)

        self.connect(self.add_button, QtCore.SIGNAL("clicked()"),
            self.add_media)
        self.connect(self.remove_button, QtCore.SIGNAL("clicked()"),
            self.remove_media)
        self.connect(self.search_line_edit, QtCore.SIGNAL("returnPressed()"),
            self.search)

        self.setTabOrder(self.search_type_combo, self.search_line_edit)
        self.setTabOrder(self.search_line_edit, self.list_view)
        self.setTabOrder(self.list_view, self.add_button)
        self.setTabOrder(self.add_button, self.remove_button)

    def add_media(self):
        """
        Add media to the XMMS2 media library.
        """
        audio_files = QtGui.QFileDialog.getOpenFileNames(
                        self,
                        "Add Audio Files",
                        getenv('HOME'),
                        "Audio (*.mp3 *.ogg *.flac)")
        # TODO: Attempt to add selected files to mlib

    def remove_media(self):
        """
        Remove media from the XMMS2 media library.
        """
        print "remove_media() called"

    def search(self):
        print "search() called"
