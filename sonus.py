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
import sonusgui


class Sonus(xmmsclient.XMMS):
    """
    This is the main Sonus class. Connection to XMMS2 is done here.
    This class also acts as a 'hub' for interfacing between the various Sonus
    modules.
    """
    def __init__(self, clientName):
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
        self.handleDisconnect = None  # TODO: Default disconnection handler

        # Connect to xmms2d
        self.xmmsConnect()

        """
        Going to need to call some classes
        signals, mlib etc
        """
        if self.isConnected():
            self.mlib = mlib.Mlib(self)
            self.playlist = playlist.Playlist(self)

    def xmmsConnect(self):
        """
        Connects to XMMS2.
        """
        try:
            path = os.getenv('XMMS_PATH')
        except KeyError:
            path = None
        try:
            self.connect(path, self.onDisconnection)
        except IOError, detail:
            self.logger.error(detail)
            self.connected = False
            return
        self.connected = True
        self.logger.info('Connected to xmms2d.')

    def isConnected(self):
        """
        Returns the status of the connection to XMMS2.
        """
        return self.connected

    def setDisconnectHandler(self, dcHndlr):
        """
        Sets the disconnect handler.
        """
        self.handleDisconnect = dcHndlr

    def onDisconnection(self, res):
        """
        Acts as a wrapper for the disconnect callback fucntion.
        """
        self.logger.critical('Forcibly disconnected from xmms2d!')
        self.handleDisconnect()


if __name__ == '__main__':
    sonus = Sonus('Sonus')
    if sonus.isConnected():
        mainWin = gui.MainWindow(sonus, sys.argv)
        sonus.setDisconnectHandler(mainWin.handleDisconnect)
        sys.exit(mainWin.run())
