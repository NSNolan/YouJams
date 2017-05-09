import os
import unittest

from YJJam import Jam, JamPlay
from YJPlaylist import Playlist

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
        Playlist.sharedPlaylist().add(token)
        
        self.assertEqual(len(os.listdir(Jam.getJamDirectory())), 1)
        self.assertTrue(os.path.exists(Jam.getJamDirectory() + token + ".mp4"))
        
        jamPlay = Playlist.sharedPlaylist().jamPlayOrder[0]

        Playlist.sharedPlaylist().remove(jamPlay.UUID)


if __name__ == "__main__":
    creationSuite = unittest.TestLoader().loadTestsFromTestCase(PlaylistCreationTests)
    unittest.TextTestRunner(verbosity=2).run(creationSuite)

    addAndRemoveSuite = unittest.TestLoader().loadTestsFromTestCase(PlaylistAddAndRemoveTests)
    unittest.TextTestRunner(verbosity=2).run(addAndRemoveSuite)


