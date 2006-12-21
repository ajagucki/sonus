"""
xmmsqt4: A Qt4 and XMMS2 connector for PyQt4
For use with Sonus, a PyQt4 XMMS2 client.

Armando Jagucki <ajagucki@gmail.com>
Reference by Tobias Rundström <tru@xmms.org>

Create an instance of the XMMSConnector class with QtCore.QCoreApplication
and xmmsclient objects as arguments, respectively.
"""

from PyQt4 import QtCore

class XMMSConnector(QtCore.QObject):
    def __init__(self, parent, xmms):
        QtCore.QObject.__init__(self, parent)
        fd = xmms.get_fd()
        self.xmms = xmms
        self.xmms.set_need_out_fun(self.check_write)

        self.rsock = \
            QtCore.QSocketNotifier(fd, QtCore.QSocketNotifier.Read, self)
        self.connect(self.rsock, QtCore.SIGNAL('activated(int)'),
                     self.handle_read)
        self.rsock.setEnabled(True)

        self.wsock = \
            QtCore.QSocketNotifier(fd, QtCore.QSocketNotifier.Write, self)
        self.connect(self.wsock, QtCore.SIGNAL('activated(int)'),
                     self.handle_write)
        self.wsock.setEnabled(False)

    def check_write(self, i):
        if self.xmms.want_ioout():
            self.toggle_write(True)
        else:
            self.toggle_write(False)

    def toggle_write(self, bool):
        self.wsock.setEnabled(bool)

    def handle_read(self, i):
        self.xmms.ioin()

    def handle_write(self, i):
        self.xmms.ioout()
