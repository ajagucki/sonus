"""
gui: Qt4 Graphical User Interface
For use with Sonus, a PyQt4 XMMS2 client.
"""

from PyQt4 import QtCore, QtGui

import xmmsqt4
import mlibgui


class MainWindow(QtGui.QMainWindow):
    def __init__(self, sonus, argv):
        self.sonus = sonus
        self.app = QtGui.QApplication(argv)
        self.app.setApplicationName('Sonus')

        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('Sonus')

        # Encapsulate our modules
        self.mlib_dialog = mlibgui.MlibDialog(self)

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
                     self.mlib_dialog.show)

    def test_button_wrapper(self):
        self.sonus.mlib.get_track_info(1, self.test_button_callback)

    def test_button_callback(self, track_info):
        if track_info is not None:
            info_str = ''
            for key in track_info:
                info_str += "%s: %s\n" % (key, track_info[key])
        else:
            info_str = 'No info dood.'
        QtGui.QMessageBox.information(self, 'Track Info', info_str,
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
