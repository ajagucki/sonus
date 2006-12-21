#!/usr/bin/python
"""
Sonus, a PyQt4 XMMS2 client.
Ben Slote <bslote@gmail.com>
Armando Jagucki <ajagucki@gmail.com>
"""

from PyQt4 import QtCore
import xmmsclient
import gui
import sys
import os
import signal

class Sonus(xmmsclient.XMMS):
    def __init__(self):
        """
        Handle SIGINT
        """
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        """
        Going to need some vars here
        status, time, current track, etc
        """
        self.connected = False
        self.disconnect_cb = None

        """
        Going to need to call some classes
        signals, mlib etc
        """

        # Initialize Sonus and connect to xmms2d
        xmmsclient.XMMS.__init__("Sonus")
        self.xmms_connect()

    def xmms_connect(self):
        try:
            path = os.getenv("XMMS_PATH")
        except KeyError:
            path = None
        try:
            print "Connecting to xmms2d...",
            self.connect(path, self.disconnect_cb_wrapper)
        except IOError, detail:
            print "\nError:", detail
            self.connected = False
            return
        print "connected successfully."
        self.connected = True

    def is_connected(self):
        return self.connected

    def set_disconnect_cb(self, dc_handler):
        self.disconnect_cb = dc_handler

    def disconnect_cb_wrapper(self, res):
        print "Sonus exiting on xmms2d disconnection."
        self.disconnect_cb()

if __name__ == "__main__":
    sonus = Sonus()
    gui = gui.Gui(sonus, sys.argv)
    sonus.set_disconnect_cb(gui.handle_disconnect)
    gui.run()
