# -*- coding: utf-8 -*-

"""
A Qt4 and XMMS2 connector for PyQt4
For use with Sonus, a PyQt4 XMMS2 client.

Armando Jagucki <ajagucki@gmail.com>
Reference by Tobias Rundström <tru@xmms.org>

Create an instance of the XMMSConnector class with QtCore.QCoreApplication
and xmmsclient objects as arguments, respectively.
"""

from PyQt4.QtCore import *


class XMMSConnector(QObject):
    """
    Handles communication with XMMS2
    """
    def __init__(self, parent, xmms):
        QObject.__init__(self, parent)
        fd = xmms.get_fd()
        self.xmms = xmms
        self.xmms.set_need_out_fun(self.checkWrite)

        self.rSock = QSocketNotifier(fd, QSocketNotifier.Read, self)
        self.connect(self.rSock, SIGNAL('activated(int)'), self.handleRead)
        self.rSock.setEnabled(True)

        self.wSock = QSocketNotifier(fd, QSocketNotifier.Write, self)
        self.connect(self.wSock, SIGNAL('activated(int)'), self.handleWrite)
        self.wSock.setEnabled(False)

    def checkWrite(self, i):
        """
        Checks if XMMS2 wants to write data
        """
        if self.xmms.want_ioout():
            self.toggleWrite(True)
        else:
            self.toggleWrite(False)

    def toggleRead(self, bool):
        """
        Toggles the read socket
        """
        self.rSock.setEnabled(bool)

    def toggleWrite(self, bool):
        """
        Togles the write socket
        """
        self.wSock.setEnabled(bool)

    def handleRead(self, i):
        """
        Handles reading
        """
        self.xmms.ioin()

    def handleWrite(self, i):
        """
        Handles writing
        """
        self.xmms.ioout()
