"""
gui: Qt4 Graphical User Interface
For use with Sonus, a PyQt4 XMMS2 client.
"""

from PyQt4 import QtGui
import xmmsqt4

class Gui(QtGui.QApplication):
    def __init__(self, sonus, argv):
        QtGui.QApplication.__init__(self, argv)

        # Connect our event loop with Sonus
        if sonus.is_connected():
            xmmsqt4.XMMSConnector(self, sonus)

    def run(self):
        """
        Show the player interface and begin the event loop
        """
        # mainWidget = MainWidget()
        # mainWidget.show()
        self.exec_()

    def handle_disconnect(self):
        self.quit()
