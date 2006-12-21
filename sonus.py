#!/usr/bin/python
"""
Sonus, a PyQt4 XMMS2 client.
Ben Slote <bslote@gmail.com>
Armando Jagucki <ajagucki@gmail.com>
"""

from PyQt4 import QtCore
from sys import argv, exit
from os import getenv
import xmmsclient
import signal
import gui

class Sonus(xmmsclient.XMMS):
    def __init__(self):
        # Handle SIGINT
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        """
        Going to need some vars here
        status, time, current track, etc
        """
        self.connected = False
        self.handle_disconnect = None  # Default disconnection handler?

        """
        Going to need to call some classes
        signals, mlib etc
        """
        self.mlib = mlib.Mlib(self)

        # Initialize Sonus and connect to xmms2d
        xmmsclient.XMMS.__init__('Sonus')
        self.xmms_connect()

    def xmms_connect(self):
        try:
            path = getenv('XMMS_PATH')
        except KeyError:
            path = None
        try:
            self.connect(path, self.on_disconnection)
        except IOError, detail:
            print 'Error:', detail
            self.connected = False
            return
        self.connected = True

    def is_connected(self):
        return self.connected

    def set_disconnect_handler(self, dc_hndlr):
        self.handle_disconnect = dc_hndlr

    def on_disconnection(self, res):
        """
        Acts as a wrapper for the disconnect callback fucntion
        """
        print 'Error: Sonus was disconnected from xmms2d!'
        self.handle_disconnect()

if __name__ == '__main__':
    sonus = Sonus()
    mainwin = gui.MainWindow(sonus, argv)
    sonus.set_disconnect_handler(mainwin.handle_disconnect)
    exit(mainwin.run())
