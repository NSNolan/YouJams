import os
import unittest

from YJJam import Jam, JamPlay
from YJPlaylist import Playlist
from threading import Thread
from time import sleep

class PlaylistCreationTests(unittest.TestCase):
    def test_sharedPlaylist(self):
        Aplaylist = Playlist.sharedPlaylist()
        Bplaylist = Playlist.sharedPlaylist()

        self.assertEqual(Aplaylist, Bplaylist)
        self.assertTrue(os.path.isdir(Jam.getJamDirectory()))
        self.assertEqual(os.listdir(Jam.getJamDirectory()), [])

class PlaylistAddAndRemoveTests(unittest.TestCase):
#    def tearDown(self):
#        Playlist.sharedPlaylist().clear()
#        Jam.removeJamDirectory()

    def test_addJamToPlaylist(self):
        token = "Cb6izAqdTnc"
        
        thread = Thread(target=Playlist.sharedPlaylist().add, args=[token])
        thread.start()
        
        thread2 = Thread(target=Playlist.sharedPlaylist().add, args=[token])
        thread2.start()
        
        Playlist.sharedPlaylist().add(token)
        
        thread.join()
        thread2.join()

#self.assertEqual(len(os.listdir(Jam.getJamDirectory())), 2)
#       self.assertTrue(os.path.exists(Jam.getJamDirectory() + token + ".mp4"))
        
        sleep(5)

if __name__ == "__main__":
    creationSuite = unittest.TestLoader().loadTestsFromTestCase(PlaylistCreationTests)
    unittest.TextTestRunner(verbosity=2).run(creationSuite)

    addAndRemoveSuite = unittest.TestLoader().loadTestsFromTestCase(PlaylistAddAndRemoveTests)
    unittest.TextTestRunner(verbosity=2).run(addAndRemoveSuite)


