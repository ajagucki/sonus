"""
gui: Qt4 Graphical User Interface
For use with Sonus, a PyQt4 XMMS2 client.
"""

from PyQt4 import QtCore, QtGui
import xmmsqt4

class MainWindow(QtGui.QMainWindow):
    def __init__(self, sonus, argv):
        self.sonus = sonus
        self.app = QtGui.QApplication(argv)
        self.app.setApplicationName('Sonus')

        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('Sonus')

        # Encapsulate our dialogs
        self.mlib_dialog = MlibDialog(self)

        # Create our widgets
        self.create_status_bar()
        self.create_test_button()

        # Connect our event loop with Sonus
        if sonus.is_connected():
            self.xmmsqt_conn = xmmsqt4.XMMSConnector(self.app, sonus)
            self.statusBar().showMessage(self.tr('Connected to xmms2d'))
        else:
            self.statusBar().showMessage(self.tr('Not connected to xmms2d'))

    def create_status_bar(self):
        self.statusBar().showMessage(self.tr('Ready'))

    def create_test_button(self):
        self.test_button = QtGui.QPushButton(self.tr('Media Library'), self)
        self.connect(self.test_button, QtCore.SIGNAL('clicked()'),
                     self.mlib_dialog_wrapper)

    def mlib_dialog_wrapper(self):
        # There might be a better way to do this
        self.mlib_dialog.resize( \
            QtCore.QSize(QtCore.QRect(0,0,650,300).size()).expandedTo( \
            self.mlib_dialog.minimumSizeHint()))
        self.mlib_dialog.show()

    def test_button_wrapper(self):
        self.sonus.mlib.get_track_info(1, self.test_button_callback)

    def test_button_callback(self, track_info):
        if track_info is not None:
            info_str = ''
            for key in track_info:
                info_str += "%s: %s\n" % (key, track_info[key])
            QtGui.QMessageBox.information(self, 'Track Info', info_str,
                                          QtGui.QMessageBox.Ok)
        else:
            QtGui.QMessageBox.information(self, 'Track Info', 'No Info Dood.',
                                          QtGui.QMessageBox.Ok)

    def run(self):
        """
        Show the main window and begin the event loop
        """
        self.show()
        return self.app.exec_()

    def handle_disconnect(self):
        """
        Handle a disconnection between Sonus and xmms2d
        """
        self.xmmsqt_conn.toggle_write(False)
        self.xmmsqt_conn.toggle_read(False)
        err_msg = QtGui.QErrorMessage(self)
        msg = self.tr('Sonus was disconnected from xmms2d, quitting.')
        err_msg.showMessage(msg)
        err_msg.exec_()
        self.app.quit()


class MlibDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.grid_layout = QtGui.QGridLayout(self)

        self.frame = QtGui.QFrame(self)

        self.grid_layout1 = QtGui.QGridLayout(self.frame)

        self.vbox_layout = QtGui.QVBoxLayout()

        self.hbox_layout = QtGui.QHBoxLayout()

        self.label = QtGui.QLabel(self.frame)
        self.hbox_layout.addWidget(self.label)
        
        self.search_type_combo = QtGui.QComboBox(self.frame)
        self.hbox_layout.addWidget(self.search_type_combo)

        self.search_line_edit = QtGui.QLineEdit(self.frame)
        self.hbox_layout.addWidget(self.search_line_edit)
        self.vbox_layout.addLayout(self.hbox_layout)

        self.list_view = QtGui.QListView(self.frame)
        self.vbox_layout.addWidget(self.list_view)
        self.grid_layout1.addLayout(self.vbox_layout, 0, 0)
        self.grid_layout.addWidget(self.frame)

        self.hbox_layout1 = QtGui.QHBoxLayout()

        spacer_item = QtGui.QSpacerItem(131, 31, QtGui.QSizePolicy.Expanding,
                                        QtGui.QSizePolicy.Minimum)
        self.hbox_layout1.addItem(spacer_item)

        self.add_button = QtGui.QPushButton(self)
        self.add_button.setObjectName("add_button")
        self.hbox_layout1.addWidget(self.add_button)

        self.remove_button = QtGui.QPushButton(self)
        self.remove_button.setObjectName("remove_button")
        self.hbox_layout1.addWidget(self.remove_button)
        self.grid_layout.addLayout(self.hbox_layout1, 1, 0)
        self.label.setBuddy(self.search_line_edit)

        self.setWindowTitle(self.tr("Media Library"))
        self.label.setText(self.tr("&Search:"))
        self.add_button.setText(self.tr("&Add"))
        self.remove_button.setText(self.tr("&Remove"))

        search_types = QtCore.QStringList(["All", "Artist", "Title", "Album"])
        self.search_type_combo.insertItems(0, search_types)

        self.connect(self.add_button, QtCore.SIGNAL("clicked()"),
            self.add_media)
        self.connect(self.remove_button, QtCore.SIGNAL("clicked()"),
            self.remove_media)

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
                        "/home",
                        "Audio (*.mp3 *.ogg *.flac)")
        # TODO: Attempt to add selected files to mlib

    def remove_media(self):
        """
        Remove media from the XMMS2 media library.
        """
        None # Not implemented
