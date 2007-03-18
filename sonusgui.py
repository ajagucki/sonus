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

        self.duration = "00:00"

        # Connect our event loop with Sonus.
        if sonus.isConnected():
            self.xmmsqtConn = xmmsqt4.XMMSConnector(self.qApp, sonus)
        else:
            self.qApp.quit()     # TODO: Allow user to attempt a reconnect

        # Create our widgets.
        self.skeletonDialog = skeletongui.SkeletonDialog(self.sonus, self)
        self.layoutWidget = QWidget(self)
        self.createPlaybackGrid()
        self.layoutWidget.setLayout(self.playbackGridLayout)
        self.setCentralWidget(self.layoutWidget)

        # Register callbacks for xmms2d broadcasts.
        self.sonus.broadcast_playback_status(self._updatePlayTrackButtonCb)
        self.sonus.broadcast_playback_current_id(self.sonus.mlib.getMediaInfoGui)
        #self.sonus.signal_playback_playtime(self._updatePlaytimeCb)

        # Get current playback status and ID
        self.sonus.playback_status(self._initPlayTrackButtonCb)
        self.sonus.playback_current_id(self.sonus.mlib.getMediaInfoGui)

        # Create the timer to get current playtime
        self.playtimeTimer = QTimer(self)


        # Listen for signal from getMediaInfoGui
        self.connect(self.sonus.mlib,
                     SIGNAL('gotMediaInfoGui(PyQt_PyObject)'),
                     self._updateLabelsCb)

        # Listen for child dialog closing
        self.connect(self.skeletonDialog,
                     SIGNAL('skeletonDialogClosed()'),
                     self._uncheckManagerCheckBoxCb)

        # Listen for the signal from self.playbackTimer
        self.connect(self.playtimeTimer, SIGNAL('timeout()'),
                     self.getPlaytime)

        # Start the playtime timer
        self.playtimeTimer.start(100)

    def createPlaybackGrid(self):
        """
        Creates the horizontal box layout for the playback widgets.
        """
        self.playbackGridLayout = QGridLayout(self.layoutWidget)

        self.infoLabel = QLabel(self)
        self.durationLabel = QLabel(self)

        self.positionSlider = QSlider(Qt.Horizontal, self)
        self.positionSlider.setMinimum(0)
        self.connect(self.positionSlider, SIGNAL('sliderReleased()'),
                     self.playbackSeek)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)

        self.playTrackButton = QPushButton(self.tr('&Play'), self)
        self.connect(self.playTrackButton, SIGNAL('clicked()'),
                     self.playTrack)

        self.previousTrackButton = QPushButton(self.tr('&Back'), self)
        self.connect(self.previousTrackButton, SIGNAL('clicked()'),
                     self.prevTrack)

        self.nextTrackButton = QPushButton(self.tr('&Next'), self)
        self.connect(self.nextTrackButton, SIGNAL('clicked()'),
                     self.nextTrack)

        self.managerCheckBox = QCheckBox(self.tr('&Manager'), self)
        self.connect(self.managerCheckBox, SIGNAL('clicked()'),
                     self.updateManagerCheckBox)

        self.buttonBox.addButton(self.playTrackButton,
                                 QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.previousTrackButton,
                                 QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.nextTrackButton,
                                 QDialogButtonBox.ActionRole)

        self.playbackGridLayout.addWidget(self.infoLabel, 1, 0, 1, 1)
        self.playbackGridLayout.addWidget(self.durationLabel, 1, 1, 1, 1)
        self.playbackGridLayout.addWidget(self.positionSlider, 2, 0, 1, 2)
        self.playbackGridLayout.addWidget(self.buttonBox, 3, 0, 1, 1)
        self.playbackGridLayout.addWidget(self.managerCheckBox, 3, 1, 1, 1)

    def _updateLabelsCb(self, trackInfo):
        """
        Updates the track information
        """
        """
        TODO: Need to either get mlib ID and query mlib for data
        or somehow look up the data from the playlist position that
        this function currently handles.
        """
        if trackInfo['artist'] == "" or trackInfo['artist'] == "(NULL)":
            artist = "Unknown"
        else:
            artist = trackInfo['artist']
        if trackInfo['title'] == "" or trackInfo['title'] == "(NULL)":
            title = "Unknown"
        else:
            title = trackInfo['title']
        if trackInfo['duration'] == "" or trackInfo['duration'] == "(NULL)":
            self.duration = "Unknown"
        else:
            self.duration = trackInfo['duration']

        self.infoLabel.setText('%s - %s' % (artist, title))
        self.durationLabel.setText('00:00/%s' % self.formatDur(self.duration))
        self.positionSlider.setMaximum(self.duration)

    def getPlaytime(self):
        self.sonus.playback_playtime(self._updatePlaytimeCb)
    
    def _updatePlaytimeCb(self, xmmsResult):
        """
        Keeps self.durationLabel updated.
        """
        if xmmsResult.iserror():
            self.logger.error('XMMS result error: %s', xmmsResult.get_error())
        else:
            msec = xmmsResult.value()
            playtime = self.formatDur(msec)
            duration = self.formatDur(self.duration)
            self.durationLabel.setText('%s/%s' % (playtime, duration))
            if not self.positionSlider.isSliderDown():
                self.positionSlider.setValue(msec)
    
    def updateManagerCheckBox(self):
        """
        Updates the manager check box.
        """
        if self.managerCheckBox.checkState():
            self.skeletonDialog.show()
        else:
            self.skeletonDialog.hide()

    def _uncheckManagerCheckBoxCb(self):
        self.managerCheckBox.setCheckState(Qt.Unchecked)

    
    def _updatePlayTrackButtonCb(self, xmmsResult):
        """
        Updates play/pause button depending on xmms2d's playback status.
        """
        if xmmsResult.value() == xmmsclient.PLAYBACK_STATUS_PAUSE or \
                        xmmsResult.value() == xmmsclient.PLAYBACK_STATUS_STOP:
           self.playTrackButton.setText(self.tr('&Play'))
        else:
            self.playTrackButton.setText(self.tr('&Pause'))
    

    def _initPlayTrackButtonCb(self, xmmsResult):
        """ 
        Updates play/pause button depending on xmms2d's playback status upon
        initialization to avoid logic problems.
        """
        if xmmsResult.value() == xmmsclient.PLAYBACK_STATUS_PAUSE or \
                        xmmsResult.value() == xmmsclient.PLAYBACK_STATUS_STOP:
            self.playTrackButton.setText(self.tr('&Play'))
        else:
            self.playTrackButton.setText(self.tr('&Pause'))

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

    def playbackSeek(self):
        """
        Seeks to a specific position (msec) of the current track.
        """
        self.sonus.playback_seek_ms(self.positionSlider.value())
    
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

    def formatDur(self, duration):
        return "%02d:%02d" % (duration/60000, (duration/1000)%60)
