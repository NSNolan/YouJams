from YJJam import Jam, JamPlay
from threading import Lock, RLock

### YJPlaylist.py
# Nolan Astrein
#
## Notes
# > Playlist is
#
# > Limitations...
#     download
#

class Playlist(object):
    singletonLock = Lock()
    singletonPlaylist = None
    
    @classmethod
    def sharedPlaylist(cls):
        if not cls.singletonPlaylist:
            with cls.singletonLock:
                if not cls.singletonPlaylist:
                    cls.singletonPlaylist = cls()
        return cls.singletonPlaylist
    
    def __init__(self):
        self.playlistRLock = RLock()

        self.jamBag = {} # Token -> Jam map of all Jams that ever attempted downloaded
        self.jamPlayOrder = []  # List of JamPlays in order
        
        Jam.createJamDirectory()
    
    def __del__(self):
        # TODO: when should the Jam directory be removed
        Jam.removeJamDirectory()
        pass
    
#    def __str__(self):
#        description = "{ "
#        
#        jamTokenDescription = "{ jamTokenOrder : "
#        for jamToken in self.jamTokenOrder:
#            jamTokenDescription += jamToken
#            jamTokenDescription += " ,"
#        jamTokenDescription =
#        
#        jamTokenOrder + " }"
#        return "{ jo"

    def add(self, token):
        assert(len(token) > 0)
        print "TRACE[Playlist.add]> Playlist add token: " + token
        
        jamToDownload = None
        downloadSucceeded = False

        with self.playlistRLock:
            jamToDownload = self._jamFromBagForToken(token)
            if jamToDownload:
                print "TRACE[Playlist.add]> Playlist already has jam in jam bag: " + str(jamToDownload)
            else:
                jamToDownload = Jam(token)
                self.jamBag[token] = jamToDownload
                print "TRACE[Playlist.add]> Playlist added jam to jam bag: " + str(jamToDownload)
            
            self.jamPlayOrder.append(jamToDownload.jamPlay())
            print "TRACE[Playlist.add]> Playlist added jam to jam order: " + str(jamToDownload)

        try:
            jamToDownload.download()
            downloadSucceeded = True
            print "TRACE[Playlist.add]> Playlist downloaded jam: " + str(jamToDownload)
        except JamDownloadError as e:
            print "ERROR[Playlist.add]> Playlist failed to download jam with exception: " + repr(e)
        
        if not downloadSucceeded:
            with self.playlistRLock:
                # Subsequent downloads of this jam may have suceeded while the first
                # jam download was in progress.  First download of any jam is responsible
                # for cleaning up the entire jam play order if it fails.  Knowing the
                # implementation details of the Jam object we can assert that the
                # if one download fails, all jam plays should be removed.
                self._removeAllJamPlaysFromOrderMatchingToken(jamToDownload.token)
                raise PlaylistAddFailureError

    def remove(self, jamPlayUUID):
        assert(len(jamPlayUUID) > 0)
        print "TRACE[Playlist.remove]> Playlist remove jam play UUID: " + jamPlayUUID
        
        jamToDelete = None
        deleteSucceeded = False
    
        with self.playlistRLock:
            jamPlayToDelete = self._removeAndReturnJamPlayFromOrderForUUID(jamPlayUUID)
            if not jamPlayToDelete:
                print "ERROR[Playlist.remove]> Playlist does not have jam play in order with UUID: " + jamPlayUUID
                raise PlaylistRemoveNoJamPlayForUUIDError
            else:
                jamToDelete = self._jamFromBagForToken(jamPlayToDelete.token)
                if not jamToDelete:
                    print "ERROR[Playlist.remove]> Playlist does not have jam in bag with UUID: " + jamPlayToDelete.token
                    raise PlaylistRemoveNoJamForTokenError
        try:
            jamToDelete.delete()
            deleteSucceeded = True
            print "TRACE[Playlist.remove]> Playlist deleted jam: " + str(jamToDelete)
        except JamDeleteError as e:
            print "ERROR[Playlist.remove]> Playlist failed to delete jam with exception: " + repr(e)
            raise PlaylistRemoveFailureError
            
    def dequeNextJamPlay(self):
        with self.playlistRLock:
            if len(self.jamPlayOrder) > 0:
                jamPlay = self.jamPlayOrder.pop(0)
                return self._jamFromBagForToken(jamPlay.token)
            return None

#    def jamPlayOrder(self):
#        with self.playlistRLock:
#            return self.jamPlayOrder
    
    def isEmpty(self):
        with self.playlistRLock:
            return self.jams == []

    def _jamFromBagForToken(self, token):
        assert(len(token) > 0)
        
        with self.playlistRLock:
            try:
                return self.jamBag[token]
            except KeyError:
                return None

    def _removeAllJamPlaysFromOrderMatchingToken(self, token):
        assert(len(token) > 0)
        
        with self.playlistRLock:
            oldOrderLength = len(self.jamTokenOrder)
            self.jamPlayOrder = [jamPlay for jamPlay in self.jamPlayOrder if jamPlay.token != token]
            newOrderLength = len(self.jamTokenOrder)

        if oldOrderLength <= newOrderLength:
            print "WARN[Playlist._removeAllJamPlaysFromOrderMatchingToken]> Playlist does not have token in Jam Play order: " + token

    def _removeAndReturnJamPlayFromOrderForUUID(self, jamPlayUUID):
        assert(len(jamPlayUUID) > 0)

        with self.playlistRLock:
            indexToRemove = None
            currentIndex = 0
            
            for jamPlay in self.jamPlayOrder:
                if jamPlay.UUID == jamPlayUUID:
                    indexToRemove = currentIndex
                    break
                currentIndex+=1

            if indexToRemove == None:
                print "WARN[Playlist._removeAndReturnJamPlayFromOrderForUUID]> Playlist does not have UUID in Jam Play order: " + jamPlayUUID
                return None

            return self.jamPlayOrder.pop(indexToRemove)
