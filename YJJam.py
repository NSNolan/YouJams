import errno
import os

from YJExceptions import *
from subprocess import call
from threading import Lock
from time import sleep
from uuid import uuid4

### YJJam.py
# Nolan Astrein
#
## Notes
# > The Jam directory should exist before downloading any jam instance
#
# > Limitations...
#     downloading a jam cannot be canceled,
#         therefor you cannot delete a jam while it is downloading the only reference to it
#     playing a jam cannot be canceled,
#         therefor you cannot delete a jam while it is playing the only reference to it
#     deleting a jam cannot be canceled,
#         therefor you cannot download a jam while it is deleting the only reference to it
#         this is due to the fact that a particular Jam is always written to the same location
#

# youtube-dl and omxplayer are not pre-installed on macOS
IS_MAC_OS       = True
IS_TESTING      = True
JAM_DIRECTORY   = os.path.expanduser('~') + "/.Jams/"

class JamPlay(object):
    def __init__(self, token):
        self.token = token
        self.UUID = str(uuid4())
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.UUID == other.UUID
        return False

class JamState(object):
    NOT_DOWNLOADED = 0
    DOWNLOADING = 1
    DOWNLOADED = 2
    PLAYING = 3
    DELETING = 4

    @staticmethod
    def stateToString(state):
        if state == JamState.NOT_DOWNLOADED:
            return "NOT DOWNLOADED"
        elif state == JamState.DOWNLOADING:
            return "DOWNLOADING"
        elif state == JamState.DOWNLOADED:
            return "DOWNLOADED"
        elif state == JamState.PLAYING:
            return "PLAYING"
        elif state == JamState.DELETING:
            return "DELETING"
        else:
            return "UNKNOWN"

class Jam(object):
    def __init__(self, token):
        self.token = token
        self.url = "https://www.youtube.com/watch?v=" + self.token
        self.filePath = JAM_DIRECTORY + self.token + ".mp4"
        
        self.state = JamState.NOT_DOWNLOADED
        self.referenceCount = 0
        
        self.jamLock = Lock()
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.token == other.token
        return False
    
    def __hash__(self):
        return hash(self.token)
    
    def __str__(self):
        return "{ token : " + self.token + ", " \
               + "state : " + JamState.stateToString(self.state) + ", " \
               + "reference count : " + str(self.referenceCount) + " }"

    def download(self):
        print "TRACE[Jam.download]> Jam download: " + str(self)

        # Start downloading barrier
        with self.jamLock:
            if self.state == JamState.NOT_DOWNLOADED:
                assert(self.referenceCount == 0)
                
                self.state = JamState.DOWNLOADING
                self.referenceCount = 1
                print "TRACE[Jam.download]> Jam started downloading: " + str(self)

            elif self.state == JamState.DOWNLOADING:
                assert(self.referenceCount > 0)

                self.referenceCount += 1
                print "TRACE[Jam.download]> Jam reference count incremented while downloading: " + str(self)
                return

            elif self.state == JamState.DOWNLOADED:
                assert(self.referenceCount > 0)
                
                self.referenceCount += 1
                print "TRACE[Jam.download]> Jam reference count incremented while downloaded: " + str(self)
                return

            elif self.state == JamState.PLAYING:
                assert(self.referenceCount > 0)
                
                self.referenceCount += 1
                print "TRACE[Jam.download]> Jam reference count incremented while playing: " + str(self)
                return

            elif self.state == JamState.DELETING:
                assert(self.referenceCount == 1)

                print "ERROR[Jam.download]> A Jam should not be downloading if it is deleting: " + str(self)
                raise JamDownloadIsDeletingError

            else:
                print "ERROR[Jam.download]> Encountered unknown Jam state " +  str(self.state) + ": " + str(self)
                raise JamUnknownStateError
                
                
        jamDirectoryExists = False
        downloadSucceeded = False
        
        # Check if Jam directory exists
        if os.path.exists(JAM_DIRECTORY):
            jamDirectoryExists = True
        else:
            print "ERROR[Jam.download]> A Jam should not be downloading if the Jam directory does not exists: " + str(self)

        if jamDirectoryExists:
            # Phony work for testing
            if IS_TESTING:
                sleep(1)
                f = open(self.filePath, 'w')
                f.write(self.url + "\n")
                f.close()
                downloadSucceeded = True
                print "TRACE[Jam.download](IS_TESTING)> Jam succeeded downloading: " + str(self)
            
            # Perform download
            else:
                # TODO: Write to ~/.Jams/
                status = call(["youtube-dl",
                               "--audio-format", "mp3",
                               "--audio-quality", "4",
                               "--extract-audio",
                               "--quiet",
                               self.url])
                
                if status == 0:
                    print "TRACE[Jam.download]> Jam succeeded downloading: " + str(self)
                    downloadSucceeded = True
                else:
                    print "ERROR[Jam.download]> youtube-dl failed with error code " + str(status) + ": " + str(self)

        # End downloading barrier
        with self.jamLock:
            assert(self.state == JamState.DOWNLOADING)
            
            if downloadSucceeded:
                self.state = JamState.DOWNLOADED
            else:
                self.state = JamState.NOT_DOWNLOADED
                self.referenceCount = 0
                print "TRACE[Jam.download]> Jam set reference count to zero due to download failure: " + str(self)
                
                if not jamDirectoryExists:
                    raise JamDownloadNoJamDirectoryError

                raise JamDownloadFailureError

            print "TRACE[Jam.download]> Jam ended downloading: " + str(self)

    def delete(self):
        print "TRACE[Jam.delete]> Jam delete: " + str(self)
        
        # Start deleting barrier
        with self.jamLock:
            if self.state == JamState.NOT_DOWNLOADED:
                assert(self.referenceCount == 0)
                
                print "ERROR[Jam.delete]> A Jam should not be deleting if it is not downloaded: " + str(self)
                raise JamDeleteNotDownloadedError
            
            elif self.state == JamState.DOWNLOADING:
                assert(self.referenceCount > 0)

                if self.referenceCount > 1:
                    self.referenceCount -= 1
                    print "TRACE[Jam.delete]> Jam reference count decremented while downloading: " + str(self)
                    return
                else:
                    print "ERROR[Jam.delete]> A Jam should not be deleting if it is downloading the only reference: " + str(self)
                    raise JamDeleteOnlyReferenceIsDownloadingError

            elif self.state == JamState.DOWNLOADED:
                assert(self.referenceCount > 0)
                
                if self.referenceCount > 1:
                    self.referenceCount -= 1
                    print "TRACE[Jam.delete]> Jam reference count decremented while downloaded: " + str(self)
                    return
                else:
                    self.state = JamState.DELETING
                    print "TRACE[Jam.delete]> Jam started deleting: " + str(self)

            elif self.state == JamState.PLAYING:
                assert(self.referenceCount > 0)
                
                if self.referenceCount > 1:
                    self.referenceCount -= 1
                    print "TRACE[Jam.delete]> Jam reference count decremented while playing: " + str(self)
                    return
                else:
                    print "ERROR[Jam.delete]> A Jam should not be deleting if it is playing the only reference: " + str(self)
                    raise JamDeleteOnlyReferenceIsPlayingError

            elif self.state == JamState.DELETING:
                assert(self.referenceCount == 1)

                print "ERROR[Jam.delete]> A Jam should not be deleting if it is deleting the only reference: " + str(self)
                raise JamDeleteOnlyReferenceIsDeletingError
    
            else:
                print "ERROR[Jam.delete]> Encountered unknown Jam state " +  str(self.state) + ": " + str(self)
                raise JamUnknownStateError

        # Phony work for testing
        if (IS_TESTING):
            sleep(1)
        
        # Perform delete
        deleteSucceeded = False
        if os.path.exists(self.filePath):
            os.remove(self.filePath)
            deleteSucceeded = True
            print "TRACE[Jam.delete]> Jam succeeded deleting: " + str(self)
        else:
            print "ERROR[Jam.delete]> A Jam was deleted that does not exist on disk: " + str(self)

        # End deleting barrier
        with self.jamLock:
            assert(self.state == JamState.DELETING)
            
            if deleteSucceeded:
                self.state = JamState.NOT_DOWNLOADED
                self.referenceCount = 0
            else:
                self.state = JamState.DOWNLOADED
                raise JamDeleteFailureError

            print "TRACE[Jam.delete]> Jam ended deleting: " + str(self)

    def play(self):
        print "TRACE[Jam.play]> Jam play: " + str(self)

        # Start playing barrier
        with self.jamLock:
            if self.state == JamState.NOT_DOWNLOADED:
                assert(self.referenceCount == 0)
            
                print "ERROR[Jam.play]> A Jam should not be playing if it is not downloaded: " + str(self)
                raise JamPlayNotDownloadedError
            
            elif self.state == JamState.DOWNLOADING:
                assert(self.referenceCount > 0)
            
                print "ERROR[Jam.play]> A Jam should not be playing if it is downloading: " + str(self)
                raise JamPlayIsDownloadingError
            
            elif self.state == JamState.DOWNLOADED:
                assert(self.referenceCount > 0)
            
                self.state = JamState.PLAYING
                print "TRACE[Jam.play]> Jam started playing: " + str(self)
            
            elif self.state == JamState.PLAYING:
                assert(self.referenceCount > 0)

                print "ERROR[Jam.play]> A Jam should not be playing if it is playing: " + str(self)
                raise JamPlayIsPlayingError

            elif self.state == JamState.DELETING:
                assert(self.referenceCount == 1)

                print "ERROR[Jam.play]> A Jam should not be played if it is deleting: " + str(self)
                raise JamPlayIsDeletingError

            else:
                print "ERROR[Jam.play]> Encountered unknown Jam state " +  str(self.state) + ": " + str(self)
                raise JamUnknownStateError
    
        playSucceeded = False
    
        # Phony work for testing
        if IS_TESTING:
            sleep(1)
            playSucceeded = True
            print "TRACE[Jam.play](IS_TESTING)> Jam succeeded playing: " + str(self)
        
        # Perform play
        else:
            # TODO: Read from ~/.Jams/
            status = call(["omxplayer",
                           "-o", "local",
                           self.filePath])
            
            if status == 0:
                print "TRACE[Jam.play]> Jam succeeded playing: " + str(self)
                playSucceeded = True
            else:
                print "ERROR[Jam.play]> omxplayer failed with error code " + str(status) + ": " + str(self)

        # End playing barrier
        with self.jamLock:
            assert(self.state == JamState.PLAYING)

            self.state = JamState.DOWNLOADED
            if not playSucceeded:
                raise JamPlayFailureError

            print "TRACE[Jam.play]> Jam ended playing: " + str(self)

    def jamPlay(self):
        return JamPlay(self.token)

    @staticmethod
    def getJamDirectory():
        return JAM_DIRECTORY

    @staticmethod
    def createJamDirectory():
        if not os.path.exists(os.path.dirname(JAM_DIRECTORY)):
            try:
                os.makedirs(os.path.dirname(JAM_DIRECTORY))
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise exception

    @staticmethod
    def removeJamDirectory():
        # Expects Jam directory to be empty
        assert(len(os.listdir(JAM_DIRECTORY)) == 0)
        os.rmdir(JAM_DIRECTORY)
