"""
mlib: Basic xmms2 medialib functions
For use with Sonus, a PyQt4 XMMS2 client.
"""

class Mlib:
    def __init__(self, sonus):
        self.sonus = sonus

    def search(self, search_type, search_string, ret):
        query = "select distinct m1.id as id from Media m1 left join Media m2 on m1.id = m2.id and m2.key = 'resolved' and m2.value = 1"

        if search_type == "all":
            query += " where lower(m1.value) like '%%%s%%'" % (search_string)
        else:
            query += " where m1.key = '%s' and lower(m1.value) like '%%%s%%'" % (search_type, search_string)

        query += " order by m1.id"
        
        handler = TrackListHandler(ret)
        self.sonus.medialib_select(query, handler.callback)

    """
    For example:
    self.Sonus.Mlib.get_track_info(track_id, callback)
    """
    def get_track_info(self, track_id, ret, *args):
        handler = TrackInfoHandler(ret, *args)
        self.sonus.medialib_get_info(track_id, handler.callback)

class TrackListHandler:
    def __init__(self, ret):
        self.ret = ret
    
    def callback(self, track_list):
        track_list = track_list.value()
        track_list = [track["id"] for track in track_list]
        
        self.ret(track_list)

class TrackInfoHandler:
    def __init__(self, ret, *args):
        self.ret = ret
        self.args = args
    
    def callback(self, track_info):
        track_info = track_info.value()
        
        self.ret(track_info, *self.args)