#!/usr/bin/python
"""
Sonus, a PyQt4 XMMS2 client.
"""

from PyQt4 import QtCore
import xmmsclient
import xmmsqt4
import sys
import os

class sonus(xmmsclient.XMMS):
    def __init__(self):
        """
        Going to need some vars here
        status, time, current track, etc
        """

        """
        Going to need to call some classes
        signals, mlib etc
        """

        # Initialize Sonus and connect to xmms2d
        xmmsclient.XMMS.__init__("Sonus")
        self.main_loop = QtCore.QCoreApplication(sys.argv)
        retcode = self.xmms_connect()
        if not retcode:
            xmmsqt4.XMMSConnector(self.main_loop, self)
        else:
            self.die()

    def __del__(self):
        self.main_loop.quit()

    def xmms_connect(self):
        try:
            path = os.getenv("XMMS_PATH")
        except KeyError:
            path = None
        try:
            print "Connecting to xmms2d...",
            self.connect(path, self.xmms_disconnect_cb)
        except IOError, detail:
            print "\nError:", detail
            return 1
        print "connected successfully."
        return 0

    def run_loop(self):
        self.main_loop.exec_()

    def xmms_disconnect_cb(self):
        print "Sonus exiting on xmms2d disconnection."
        self.main_loop.quit()
        self.die()

    def die(self):
        """
        The main_loop will quit on __del__ implicitly
        """
        # self.main_loop.quit()
        sys.exit()

if __name__ == "__main__":
    sonus = sonus()
    """
    If we run the loop below, and xmms2d quits, it is not handled gracefully,
    even though we have set a disconnect callback. However, the same thing
    happens in the tutorial program that uses xmmsglib!
    """
    #sonus.run_loop()
