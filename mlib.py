"""
mlib: Basic xmms2 medialib functions
For use with Sonus, a PyQt4 XMMS2 client.
"""

class Mlib:
    def __init__(self, sonus):
        self.sonus = sonus
        self.idList = []

    def get_all_media(self):
        """
        Order up a list of all the tracks in the media library
        """
        allmedia = Universe()
        print "From getAllMedia():", allmedia   #DEBUG
        self.sonus.coll_query_ids(allmedia, cb=self.callback)

    def callback(self, result):
        """
        Callback for the collection query
        """
        print "From callback():", result    #DEBUG
        if not result.iserror():
            self.idList = result.value()
        else:
            self.idList = ['error']    #TODO: Raise exception?

        """
        Now we want to try and emit a signal to inform the gui
        """
        print "mlibmodel: Emitting singal 'got_all_media()'"    #DEBUG
        self.emit(QtCore.SIGNAL('got_all_media()'))
