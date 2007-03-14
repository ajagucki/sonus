"""
Media library model for mlibgui.MlibDialog's QTableView
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *

from supermodel import *


class MlibModel(SuperModel):
    """
    The MlibModel class handles the media library model. This includes
    initializing it and handling the signals that keep it up to date.
    """
    def __init__(self, sonus, parent=None):
        SuperModel.__init__(self, parent)
        self.sonus = sonus
        self.logger = logging.getLogger('Sonus.mlibmodel')

        self.propertiesList = ['id', 'artist', 'title', 'album']

        # Setup our connections
        self.connect(self.sonus.collections,
                     SIGNAL('gotAllCollInfos(PyQt_PyObject)'),
                     self.initModelData)
        self.connect(self.sonus.mlib, SIGNAL('gotMediaInfo(PyQt_PyObject)'),
                     self.addOrUpdateEntry)
        self.connect(self.sonus.collections,
                     SIGNAL('searchedCollInfos(PyQt_PyObject)'),
                     self.replaceModelData)

        # Initiaize our data
        self.sonus.collections.getAllCollInfos(self.propertiesList)

    def initModelData(self, newInfoList):
        """
        Sets up the data that the model provides to a current copy from mlib.
        """
        self.replaceModelData(newInfoList)
        self.emit(SIGNAL('modelInitialized()'))

        # We only initialize once, so stop monitoring this signal.
        self.disconnect(self.sonus.collections,
                        SIGNAL('gotAllCollInfos(PyQt_PyObject)'),
                        self.initModelData)
