"""
Sonus' main graphical user interface.
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import xmmsclient

import xmmsqt4
import skeletongui


class MainWindow(QMainWindow):
    """
    The main window with a QApplication housing the event loop.
    """
    def __init__(self, sonus, argv):
        """
        MainWindow's constructor sets up its Qt event loop connecting it to
        xmms2, creates all of its widgets setting up their connections, and
        performs other initializations.
        """
        self.qApp = QApplication(argv)
        self.qApp.setApplicationName('Sonus')
        QMainWindow.__init__(self)
        self.setWindowTitle('Sonus')
        self.sonus = sonus
        self.logger = logging.getLogger('Sonus.sonusgui')

        # Connect our event loop with Sonus.
        if sonus.isConnected():
            self.xmmsqtConn = xmmsqt4.XMMSConnector(self.qApp, sonus)
        else:
            self.qApp.quit()     # TODO: Allow user to attempt a reconnect

        # Create our widgets.
        self.skeletonDialog = skeletongui.SkeletonDialog(self.sonus, self)
        self.layoutWidget = QWidget(self)
        self.createPlaybackHbox()
        self.layoutWidget.setLayout(self.playbackHBoxLayout)
        self.setCentralWidget(self.layoutWidget)

        # Register callbacks for xmms2d broadcasts.
        self.sonus.broadcast_playback_status(self.updatePlayTrackButton)

    def createPlaybackHbox(self):
        """
        Creates the horizontal box layout for the playback widgets.
        """
        self.playbackHBoxLayout = QHBoxLayout(self.layoutWidget)

        self.positionSlider = QSlider(Qt.Horizontal,self)

        self.playTrackButton = QPushButton(self.tr('&Play'), self)
        self.connect(self.playTrackButton, SIGNAL('clicked()'), self.playTrack)

        self.previousTrackButton = QPushButton(self.tr('&Back'), self)
        self.connect(self.previousTrackButton, SIGNAL('clicked()'), 
                     self.prevTrack)

        self.nextTrackButton = QPushButton(self.tr('&Next'), self)
        self.connect(self.nextTrackButton, SIGNAL('clicked()'), self.nextTrack)

        self.managerCheckBox = QCheckBox(self.tr('&Manager'), self)
        self.connect(self.managerCheckBox, SIGNAL('clicked()'),
                     self.updateManagerCheckBox)

        self.playbackHBoxLayout.addWidget(self.playTrackButton)
        self.playbackHBoxLayout.addWidget(self.previousTrackButton)
        self.playbackHBoxLayout.addWidget(self.nextTrackButton)
        self.playbackHBoxLayout.addWidget(self.positionSlider)
        self.playbackHBoxLayout.addWidget(self.managerCheckBox)

    def updateManagerCheckBox(self):
        """
        Updates the manager check box.
        """
        if self.managerCheckBox.checkState():
            self.skeletonDialog.show()
        else:
            self.skeletonDialog.hide()

    def updatePlayTrackButton(self, xmmsResult):
        """
        Updates play/pause button depending on xmms2d's playback status.
        """
        if xmmsResult.value() == xmmsclient.PLAYBACK_STATUS_PLAY:
           self.playTrackButton.setText(self.tr('&Pause'))
        else:
            self.playTrackButton.setText(self.tr('&Play'))

    def nextTrack(self):
        """
        Starts playing the next track in the playlist.
        """
        self.sonus.playlist_set_next_rel(1)
        self.sonus.playback_tickle()
        
    def prevTrack(self):
        """
        Starts playing the previous track in the playlist.
        """
        self.sonus.playlist_set_next_rel(-1)
        self.sonus.playback_tickle()

    def playTrack(self):
        """
        Plays or pauses the current track in the playlist.
        """
        if self.playTrackButton.text() == self.tr('&Pause'):
            self.sonus.playback_pause()
            self.logger.info('Pausing current track.')
        else:
            self.sonus.playback_start()
            self.logger.info('Playing current track.')

    def run(self):
        """
        Show the main window and begin the event loop.
        """
        self.show()
        return self.qApp.exec_()

    def handleDisconnect(self):
        """
        Handle a disconnection between Sonus and xmms2d.
        """
        self.xmmsqtConn.toggleWrite(False)
        self.xmmsqtConn.toggleRead(False)
        errMsg = QErrorMessage(self)
        msg = self.tr('Sonus was disconnected from xmms2d, quitting.')
        errMsg.showMessage(msg)
        errMsg.exec_()
        self.qApp.quit()

    def closeEvent(self, event):
        """
        Reimplemented to handle the close event ourselves, allowing us to
        force any open child dialogs to close, as well as perform clean up
        tasks.
        """
        QMainWindow.closeEvent(self, event)
        self.qApp.quit()
