"""
mlib: Basic xmms2 medialib functions
For use with Sonus, a PyQt4 XMMS2 client.
"""

class Mlib:
    def __init__(self, sonus):
        self.sonus = sonus

    def search(self, search_type, search_string, ret):
        query  = "SELECT DISTINCT m1.id AS id FROM Media m1 LEFT JOIN "
        query += "Media m2 ON m1.id = m2.id AND m2.key = 'resolved' AND "
        query += "m2.value = 1 "

        if search_type == "all":
            query += "WHERE lower(m1.value) LIKE '%%%s%%' " % (search_string)
        else:
            query += "WHERE m1.key = '%s' AND lower(m1.value) LIKE '%%%s%%' " \
                   % (search_type, search_string)

        query += "ORDER BY m1.id"

        handler = TrackListHandler(ret)
        self.sonus.medialib_select(query, handler.callback)

    """
    For example:
    self.sonus.mlib.get_track_info(track_id, callback)
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