"""
gui: Qt4 Graphical User Interface
For use with Sonus, a PyQt4 XMMS2 client.
"""

from PyQt4 import QtGui
import xmmsqt4

class MainWindow(QtGui.QMainWindow):
    def __init__(self, sonus, argv):
        self.app = QtGui.QApplication(argv)
        self.app.setApplicationName('Sonus')

        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('Sonus')

        # Create our widgets
        self.createStatusBar()

        # Connect our event loop with Sonus
        if sonus.is_connected():
            xmmsqt4.XMMSConnector(self.app, sonus)
            self.statusBar().showMessage(self.tr('Connected to xmms2d'))
        else:
            self.statusBar().showMessage(self.tr('Not connected to xmms2d'))

    def createStatusBar(self):
        self.statusBar().showMessage(self.tr('Ready'))

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
        self.app.quit()
