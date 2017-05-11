from YJExceptions import *
from YJJam import Jam, JamPlay
from threading import Lock, RLock, Thread

### YJPlaylist.py
# Nolan Astrein
#
## Notes
# > Playlist
#
# > Limitations...
#
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
        
        self.isPlaying = False

        self.jamBag = {} # Token -> Jam map of all Jams that ever attempted download
        self.jamPlayOrder = []  # List of JamPlays in order
        
        Jam.createJamDirectory()
    
    def __del__(self):
        # TODO: when should the Jam directory be removed
        Jam.removeJamDirectory()
        pass
    
    def __str__(self):
        description = "{ "
        
        # Add JamPlay order to description
        jamPlayOrder = "jamPlayOrder : ["
        for jamPlay in self.jamPlayOrder:
            jamPlayOrder += (jamPlay.token + "." + jamPlay.UUID + ", ")
        jamPlayOrder += "]"
        description += jamPlayOrder
        
        description += " }"
        return description

    def add(self, token):
        assert(len(token) > 0)
        print "TRACE[Playlist.add]> Playlist add " + token + ": " + str(self)
        
        jamToDownload = None

        with self.playlistRLock:
            jamToDownload = self._jamFromBagForToken(token)
            if jamToDownload:
                print "TRACE[Playlist.add]> Playlist already has jam in jam bag: " + str(self)
            else:
                jamToDownload = Jam(token)
                self.jamBag[token] = jamToDownload
                print "TRACE[Playlist.add]> Playlist added jam to jam bag: " + str(self)
            
            self.jamPlayOrder.append(jamToDownload.jamPlay())
            print "TRACE[Playlist.add]> Playlist added jam to jam order: " + str(self)

        downloadSucceeded = False
        try:
            jamToDownload.download()
            downloadSucceeded = True
            print "TRACE[Playlist.add]> Playlist succeeded downloading jam: " + str(self)
        except JamDownloadError as exception:
            print "ERROR[Playlist.add]> Playlist failed downloading jam with exception: " + repr(exception)

        # If download succeeds, start playing the playlist
        # Otherwise, clean up Jam play order
        if downloadSucceeded:
            self._play()
        else:
            with self.playlistRLock:
                # Subsequent downloads of this Jam may have suceeded while the first
                # Jam download was in progress.  First download of any jam is responsible
                # for cleaning up the entire Jam play order if it fails.  Knowing the
                # implementation details of the Jam object we can assert that if one
                # download of a particular Jam fails, all Jam plays references
                # should be removed from the Jam play order.
                self._removeAllJamPlaysFromOrderMatchingToken(jamToDownload.token)
                raise PlaylistAddFailureError

    def remove(self, jamPlayUUID):
        assert(len(jamPlayUUID) > 0)
        print "TRACE[Playlist.remove]> Playlist remove " + jamPlayUUID + ": " + str(self)
        
        jamToDelete = None
        
        with self.playlistRLock:
            jamPlayToDelete = self._removeAndReturnJamPlayFromOrderForUUID(jamPlayUUID)
            if not jamPlayToDelete:
                print "ERROR[Playlist.remove]> Playlist does not have jam play in order for UUID " + jamPlayUUID + ": " + str(self)
                raise PlaylistRemoveNoJamPlayForUUIDError

            jamToDelete = self._jamFromBagForToken(jamPlayToDelete.token)
            if not jamToDelete:
                print "ERROR[Playlist.remove]> Playlist does not have jam in bag for token " + jamPlayToDelete.token + ": " + str(self)
                raise PlaylistRemoveNoJamForTokenError
        
        try:
            jamToDelete.delete()
            print "TRACE[Playlist.remove]> Playlist succeeded deleting jam: " + str(self)
        except JamDeleteError as exception:
            print "ERROR[Playlist.remove]> Playlist failed deleting jam with exception: " + repr(exception)
            raise PlaylistRemoveFailureError

#    Queried by clients to get playlist details
#    def jamOrderDetails(self):
#        with self.playlistRLock:
#            return self.jamPlayOrder

    def _play(self):
        with self.playlistRLock:
            if self.isPlaying:
                print "TRACE[Playlist._play]> Playlist is already playing: " + str(self)
                return
            else:
                self.isPlaying = True
                print "TRACE[Playlist._play]> Playlist is now playing: " + str(self)

        # Run play loop on seperate thread
        thread = Thread(target=self._runPlayLoop)
        thread.start()

    def _runPlayLoop(self):
        # Walk through the Jam play order and attempt to play each Jam
        # If the Jam fails to play because it is downloading, skip it
        # If the Jam fails to play otherwise, stop the play loop
        # Once we successfully play a Jam, remove the Jam from the Playlist
        # and start looping at the beginning of the Jam play order to play
        # Jams that may have skipped along the way
        
        currentIndex = 0

        while True:
            
            nextJamPlay = None
            nextJam = None
            
            with self.playlistRLock:
                nextJamPlay = self._jamPlayForIndex(currentIndex)
                if not nextJamPlay:
                    self.isPlaying = False
                    print "TRACE[Playlist._runPlayLoop]> Playlist has no more playable Jams in Jam order: " + str(self)
                    break
            
                nextJam = self._jamFromBagForToken(nextJamPlay.token)
                if not nextJam:
                    self.isPlaying = False
                    print "ERROR[Playlist._runPlayLoop]> Playlist does not have Jam in bag for token " + nextJam.token + ": " + str(self)
                    break
        
            playSucceeded = False
            try:
                nextJam.play()
                playSucceeded = True
                print "ERROR[Playlist._runPlayLoop]> Playlist succeeded playing jam: " + str(self)
               
                # Reset current index to beginning of Jam play order once we
                # successfully play a jam, we may have skipped others while
                # looking for a Jam ready to play
                currentIndex = 0
            except JamPlayError as exception:
                if type(exception) == JamPlayIsDownloadingError:
                    print "TRACE[Playlist._runPlayLoop]> Playlist is skipping jam because it is downloading: " + str(self)
                    currentIndex += 1
                    continue
                else:
                    # Failed for unexpected reason, jam should be removed
                    print "ERROR[Playlist._runPlayLoop]> Playlist failed to play jam with exception: " + repr(exception)
            
            if playSucceeded:
                # TODO: Deleting the Jam here is blocking the play loop thread
                # If we delete this jam on another thread it may be play
                # again before it is deleted from the Jam play order
                self.remove(nextJamPlay.UUID)
            else:
                with self.playlistRLock:
                    self.isPlaying = False
    
    def _jamPlayForIndex(self, index):
        assert(index >= 0)
        
        with self.playlistRLock:
            try:
                return self.jamPlayOrder[index]
            except IndexError:
                return None
    
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
        
        indexToRemove = 0

        with self.playlistRLock:
            for jamPlay in self.jamPlayOrder:
                if jamPlay.UUID == jamPlayUUID:
                    break
                
                indexToRemove+=1

            if indexToRemove == len(self.jamPlayOrder):
                print "WARN[Playlist._removeAndReturnJamPlayFromOrderForUUID]> Playlist does not have UUID in Jam Play order: " + jamPlayUUID
                return None

            return self.jamPlayOrder.pop(indexToRemove)
