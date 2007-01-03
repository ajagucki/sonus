"""
mlibmodel: Media library model for mlibgui.MlibDialog's QTableView
For use with Sonus, a PyQt4 XMMS2 client.
"""

import logging

from PyQt4.QtCore import *

from supermodel import *


class MlibModel(SuperModel):
    def __init__(self, sonus, parent=None):
        SuperModel.__init__(self, parent)
        self.sonus = sonus
        self.logger = logging.getLogger('Sonus.mlibmodel')

        self.properties_list = ['id', 'artist', 'title', 'album']

        # Setup our connections
        self.connect(self.sonus.mlib,
                     SIGNAL('got_all_media_infos(PyQt_PyObject)'),
                     self.initModelData)
        self.connect(self.sonus.mlib, SIGNAL('got_media_info(PyQt_PyObject)'),
                     self.addEntryToModel)
        self.connect(self.sonus.mlib,
                     SIGNAL('searched_media_infos(PyQt_PyObject)'),
                     self.replaceModelData)

        # Initiaize our data
        self.sonus.mlib.get_all_media_infos(self.properties_list)

    def initModelData(self, new_info_list):
        """
        Sets up the data that the model provides to a current copy from mlib.
        """
        self.entry_info_list = new_info_list
        self.emit(SIGNAL('model_initialized()'))

        # We only initialize once, so ignore future signals.
        self.disconnect(self.sonus.mlib,
                        SIGNAL('got_all_media_infos(PyQt_PyObject)'),
                        self.initModelData)
