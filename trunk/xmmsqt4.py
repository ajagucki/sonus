# -*- coding: utf-8 -*-

"""
xmmsqt4: A Qt4 and XMMS2 connector for PyQt4
For use with Sonus, a PyQt4 XMMS2 client.

Armando Jagucki <ajagucki@gmail.com>
Reference by Tobias Rundström <tru@xmms.org>

Create an instance of the XMMSConnector class with QtCore.QCoreApplication
and xmmsclient objects as arguments, respectively.
"""

from PyQt4.QtCore import *


class XMMSConnector(QObject):
    def __init__(self, parent, xmms):
        QObject.__init__(self, parent)
        fd = xmms.get_fd()
        self.xmms = xmms
        self.xmms.set_need_out_fun(self.check_write)

        self.r_sock = QSocketNotifier(fd, QSocketNotifier.Read, self)
        self.connect(self.r_sock, SIGNAL('activated(int)'), self.handle_read)
        self.r_sock.setEnabled(True)

        self.w_sock = QSocketNotifier(fd, QSocketNotifier.Write, self)
        self.connect(self.w_sock, SIGNAL('activated(int)'), self.handle_write)
        self.w_sock.setEnabled(False)

    def check_write(self, i):
        if self.xmms.want_ioout():
            self.toggle_write(True)
        else:
            self.toggle_write(False)

    def toggle_read(self, bool):
        self.r_sock.setEnabled(bool)

    def toggle_write(self, bool):
        self.w_sock.setEnabled(bool)

    def handle_read(self, i):
        self.xmms.ioin()

    def handle_write(self, i):
        self.xmms.ioout()
