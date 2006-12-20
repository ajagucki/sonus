#!/usr/bin/python
"""
Sonus
"""
from PyQt4 import QtCore
import xmmsclient
import xmmsqt4
import os
import sys

class sonus(xmmsclient.XMMS):
	def __init__(self):
		# Going to need some vars here
		# status, time, current track, etc
		self.qt_loop = QtCore.QCoreApplication(sys.argv)
		
		# Going to need to call some classes
		# signals, mlib etc
		
		xmmsclient.XMMS.__init__("Sonus")
		self.xmms_connect()
		
		# call gui shit here
		# self.gui = sonus_gui.gui(self)
		# self.gui.exec_()
		# or whatever
		self.qt_loop._exec()
		
	
	def xmms_connect(self):
		try:
			path = os.envrion["XMMS_PATH"]
		except KeyError:
			path = None
		try:
			self.connect(path, self.xmms_disconnect_cb)
			xmmsqt4.QtConnector(self)
		except IOError:
			print "xmms2 not running\n"
			sys.exit()
	
	def xmms_disconnect_cb(self):
		print "Sonus exiting."
		self.die()
	
	def die(self):
		self.qtloop.quit()

if __name__ == "__main__":
	sonus = sonus()