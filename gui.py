"""
gui: The main window with a QApplication housing the event loop.
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import xmmsclient

import xmmsqt4
import skeletongui


class MainWindow(QMainWindow):
    def __init__(self, sonus, argv):
        self.sonus = sonus
        self.logger = logging.getLogger('Sonus.gui')
        self.app = QApplication(argv)
        self.app.setApplicationName('Sonus')

        QMainWindow.__init__(self)
        self.setWindowTitle('Sonus')

        # Connect our event loop with Sonus
        if sonus.is_connected():
            self.xmmsqt_conn = xmmsqt4.XMMSConnector(self.app, sonus)
        else:
            self.app.quit()     # TODO: Allow user to attempt a reconnect

        # Encapsulate our modules
        self.skeleton_dialog = skeletongui.SkeletonGui(self.sonus, self)

        # Create our widgets
        self.layout_widget = QWidget(self)
        self.create_playback_hbox()
        self.layout_widget.setLayout(self.playback_hbox)
        self.setCentralWidget(self.layout_widget)

        # Send XMMS our callbacks
        self.sonus.broadcast_playback_status(self.update_play_button)

    def create_playback_hbox(self):
        self.playback_hbox = QHBoxLayout(self.layout_widget)

        self.position_slider = QSlider(Qt.Horizontal,self)

        self.play_button = QPushButton(self.tr('&Play'), self)
        self.connect(self.play_button, SIGNAL('clicked()'), self.play_track)

        self.previous_button = QPushButton(self.tr('&Back'), self)

        self.forward_button = QPushButton(self.tr('&Next'), self)
        self.connect(self.forward_button, SIGNAL('clicked()'), self.next_track)

        self.mlib_checkbox = QCheckBox(self.tr('&Media Library'), self)
        self.connect(self.mlib_checkbox, SIGNAL('clicked()'),
                     self.update_mlib_checkbox)

        self.playback_hbox.addWidget(self.play_button)
        self.playback_hbox.addWidget(self.previous_button)
        self.playback_hbox.addWidget(self.forward_button)
        self.playback_hbox.addWidget(self.position_slider)
        self.playback_hbox.addWidget(self.mlib_checkbox)

    def update_mlib_checkbox(self):
        if self.mlib_checkbox.checkState():
            self.skeleton_dialog.show()
        else:
            self.skeleton_dialog.hide()

    def update_play_button(self, xmms_result):
        """
        Update Play/Pause button depending on xmms2d's playback status.
        """
        if xmms_result.value() == xmmsclient.PLAYBACK_STATUS_PLAY:
           self.play_button.setText(self.tr('&Pause'))
        else:
            self.play_button.setText(self.tr('&Play'))

    def next_track(self):
        self.sonus.playback_tickle()

    def play_track(self):
        """
        Play or Pause current track.
        """
        if self.play_button.text() == self.tr('&Pause'):
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
        return self.app.exec_()

    def handle_disconnect(self):
        """
        Handle a disconnection between Sonus and xmms2d.
        """
        self.xmmsqt_conn.toggle_write(False)
        self.xmmsqt_conn.toggle_read(False)
        err_msg = QErrorMessage(self)
        msg = self.tr('Sonus was disconnected from xmms2d, quitting.')
        err_msg.showMessage(msg)
        err_msg.exec_()
        self.app.quit()

    def closeEvent(self, event=QCloseEvent()):
        """
        Reimplemented to handle the close event ourselves, allowing us to
        force any open child dialogs to close, as well as perform clean up
        tasks.
        """
        self.app.quit()
