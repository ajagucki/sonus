#!/usr/bin/python

"""
Sonus, a PyQt4 XMMS2 client.
Ben Slote <bslote@gmail.com>
Armando Jagucki <ajagucki@gmail.com>
"""

import logging.config
import logging
import signal
import sys
import os

import xmmsclient

import mlib
import playlist
import gui
import skeletongui
import mlibgui


class Sonus(xmmsclient.XMMS):
    def __init__(self, clientname):
        # Handle SIGINT
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        # Set up the logger
        logging.config.fileConfig('logging.conf') # TODO: If file doesn't exist
        self.logger = logging.getLogger('Sonus')

        """
        Going to need some vars here
        status, time, current track, etc
        """
        self.connected = False
        self.handle_disconnect = None  # TODO: Default disconnection handler

        # Connect to xmms2d
        self.xmms_connect()

        """
        Going to need to call some classes
        signals, mlib etc
        """
        if self.is_connected():
            self.mlib = mlib.Mlib(self)
            self.playlist = playlist.Playlist(self)

    def xmms_connect(self):
        try:
            path = os.getenv('XMMS_PATH')
        except KeyError:
            path = None
        try:
            self.connect(path, self.on_disconnection)
        except IOError, detail:
            self.logger.error(detail)
            self.connected = False
            return
        self.connected = True
        self.logger.info('Connected to xmms2d.')

    def is_connected(self):
        return self.connected

    def set_disconnect_handler(self, dc_hndlr):
        self.handle_disconnect = dc_hndlr

    def on_disconnection(self, res):
        """
        Acts as a wrapper for the disconnect callback fucntion
        """
        self.logger.critical('Forcibly disconnected from xmms2d!')
        self.handle_disconnect()


if __name__ == '__main__':
    sonus = Sonus('Sonus')
    if sonus.is_connected():
        mainwin = gui.MainWindow(sonus, sys.argv)
        sonus.set_disconnect_handler(mainwin.handle_disconnect)
        sys.exit(mainwin.run())
