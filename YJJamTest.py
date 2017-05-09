import unittest

from YJJam import *
from os import path
from threading import Thread
from time import sleep

class JamTests(unittest.TestCase):
    def setUp(self):
        Jam.createJamDirectory()
    
    def tearDown(self):
        Jam.removeJamDirectory()
    
class JamSimpleTests(JamTests):
    def test_JamEquality(self):
        tokenA = "Cb6izAqdTnc-A"
        jamA1 = Jam(tokenA)
        jamA2 = Jam(tokenA)
        self.assertEqual(jamA1, jamA2)
    
        tokenB = "Cb6izAqdTnc-B"
        jamB = Jam(tokenB)
        self.assertNotEqual(jamA1, jamB)
    
    def test_JamPlayEquality(self):
        token = "Cb6izAqdTnc"
        jam = Jam(token)
        
        jamPlay1 = jam.jamPlay()
        jamPlay2 = jam.jamPlay()
        self.assertNotEqual(jamPlay1, jamPlay2)
    
    def test_JamUrls(self):
        tokenA = "Cb6izAqdTnc-A"
        jamA = Jam(tokenA)
        self.assertEqual(jamA.url, "https://www.youtube.com/watch?v=Cb6izAqdTnc-A")
    
        tokenB = "Cb6izAqdTnc-B"
        jamB = Jam(tokenB)
        self.assertEqual(jamB.url, "https://www.youtube.com/watch?v=Cb6izAqdTnc-B")
    
    def test_JamPlayEquality(self):
        token = "Cb6izAqdTnc"
        jam = Jam(token)

        jamPlay1 = jam.jamPlay()
        jamPlay2 = jam.jamPlay()
        self.assertNotEqual(jamPlay1, jamPlay2)
    
    def test_JamDownloadPlayDelete(self):
        token = "Cb6izAqdTnc"
        jam = Jam(token)
        
        try:
            self.assertEqual(jam.state, JamState.NOT_DOWNLOADED)

            jam.download()
            self.assertEqual(jam.state, JamState.DOWNLOADED)
            self.assertTrue(path.exists(Jam.getJamDirectory() + token + ".mp4"))

            jam.play()
            self.assertEqual(jam.state, JamState.DOWNLOADED)

            jam.delete()
            self.assertEqual(jam.state, JamState.NOT_DOWNLOADED)
            self.assertFalse(path.exists(Jam.getJamDirectory() + token + ".mp4"))
        
        except JamError as e:
            self.fail("test_JamDownloadPlayDelete failed with exception" + repr(e))

    def test_JamMultipleDownloadDelete(self):
        token = "Cb6izAqdTnc"
        jam = Jam(token)
        
        try:
            for x in range(0, 5):
                jam.download()
                self.assertEqual(jam.state, JamState.DOWNLOADED)
                self.assertTrue(path.exists(Jam.getJamDirectory() + token + ".mp4"))
            
            for x in range(0, 4):
                jam.delete()
                self.assertEqual(jam.state, JamState.DOWNLOADED)
                self.assertTrue(path.exists(Jam.getJamDirectory() + token + ".mp4"))

            jam.play()
            self.assertEqual(jam.state, JamState.DOWNLOADED)

            jam.delete()
            self.assertEqual(jam.state, JamState.NOT_DOWNLOADED)
            self.assertFalse(path.exists(Jam.getJamDirectory() + token + ".mp4"))

        except JamError as e:
            self.fail("test_JamMultipleDownloadDelete failed with exception" + repr(e))

class JamDownloadErrorTests(JamTests):
    def test_JamDownloadNoJamDirectoryError(self):
        token = "Cb6izAqdTnc"
        jam = Jam(token)
        
        Jam.removeJamDirectory()
    
        try:
            self.assertRaises(JamDownloadNoJamDirectoryError, jam.download)
    
        except JamError as e:
            self.fail("test_JamDownloadNoJamDirectoryError failed with exception" + repr(e))
        
        Jam.createJamDirectory()
    
    def test_JamDownloadIsDeletingError(self):
        token = "Cb6izAqdTnc"
        jam = Jam(token)

        try:
            jam.download()
            
            thread = Thread(target=jam.delete)
            thread.start()
            sleep(0.25)
            self.assertRaises(JamDownloadIsDeletingError, jam.download)
            thread.join()
            
            self.assertFalse(path.exists(Jam.getJamDirectory() + token + ".mp4"))
        
        except JamError as e:
            self.fail("test_JamDownloadIsDeletingError failed with exception" + repr(e))

class JamDeleteErrorTests(JamTests):
    def test_JamDeleteNotDownloadedError(self):
        token = "Cb6izAqdTnc"
        jam = Jam(token)
        self.assertRaises(JamDeleteNotDownloadedError, jam.delete)

    def test_JamDeleteOnlyReferenceIsDownloadingError(self):
        token = "Cb6izAqdTnc"
        jam = Jam(token)
        
        try:
            thread = Thread(target=jam.download)
            thread.start()
            sleep(0.25)
            self.assertRaises(JamDeleteOnlyReferenceIsDownloadingError, jam.delete)
            thread.join()
        
            jam.delete()
            self.assertFalse(path.exists(Jam.getJamDirectory() + token + ".mp4"))

        except JamError as e:
            self.fail("test_JamDeleteOnlyReferenceIsDownloadingError failed with exception" + repr(e))

    def test_JamDeleteOnlyReferenceIsPlayingError(self):
        token = "Cb6izAqdTnc"
        jam = Jam(token)
        
        try:
            jam.download()
            
            thread = Thread(target=jam.play)
            thread.start()
            sleep(0.25)
            self.assertRaises(JamDeleteOnlyReferenceIsPlayingError, jam.delete)
            thread.join()
        
            jam.delete()
            self.assertFalse(path.exists(Jam.getJamDirectory() + token + ".mp4"))
        
        except JamError as e:
            self.fail("test_JamDeleteOnlyReferenceIsPlayingError failed with exception" + repr(e))

    def test_JamDeleteOnlyReferenceIsDeletingError(self):
        token = "Cb6izAqdTnc"
        jam = Jam(token)
        
        try:
            jam.download()
            
            thread = Thread(target=jam.delete)
            thread.start()
            sleep(0.25)
            self.assertRaises(JamDeleteOnlyReferenceIsDeletingError, jam.delete)
            thread.join()
            
            self.assertFalse(path.exists(Jam.getJamDirectory() + token + ".mp4"))
        
        except JamError as e:
            self.fail("test_JamDeleteOnlyReferenceIsDeletingError failed with exception" + repr(e))

class JamPlayErrorTests(JamTests):
    def test_JamPlayNotDownloadedError(self):
        token = "Cb6izAqdTnc"
        jam = Jam(token)
        self.assertRaises(JamPlayNotDownloadedError, jam.play)

    def test_JamPlayIsDownloadingError(self):
        token = "Cb6izAqdTnc"
        jam = Jam(token)
        
        try:
            thread1 = Thread(target=jam.download)
            thread1.start()
            sleep(0.25)
            self.assertRaises(JamPlayIsDownloadingError, jam.play)
            thread1.join()
            
            jam.delete()
            self.assertFalse(path.exists(Jam.getJamDirectory() + token + ".mp4"))

        except JamError as e:
            self.fail("test_JamPlayIsDownloadingError failed with exception" + repr(e))

    def test_JamPlayIsPlayingError(self):
        token = "Cb6izAqdTnc"
        jam = Jam(token)
        
        try:
            jam.download()
            
            thread = Thread(target=jam.play)
            thread.start()
            sleep(0.25)
            self.assertRaises(JamPlayIsPlayingError, jam.play)
            thread.join()
            
            jam.delete()
            self.assertFalse(path.exists(Jam.getJamDirectory() + token + ".mp4"))

        except JamError as e:
            self.fail("test_JamPlayIsPlayingError failed with exception" + repr(e))

    def test_JamPlayIsDeletingError(self):
        token = "Cb6izAqdTnc"
        jam = Jam(token)
        
        try:
            jam.download()
            
            thread = Thread(target=jam.delete)
            thread.start()
            sleep(0.25)
            self.assertRaises(JamPlayIsDeletingError, jam.play)
            thread.join()

            self.assertFalse(path.exists(Jam.getJamDirectory() + token + ".mp4"))

        except JamError as e:
            self.fail("test_JamPlayIsDeletingError failed with exception" + repr(e))

if __name__ == "__main__":
    
    jamSimpleSuite = unittest.TestLoader().loadTestsFromTestCase(JamSimpleTests)
    jamDownloadErrorSuite = unittest.TestLoader().loadTestsFromTestCase(JamDownloadErrorTests)
    jamDeleteErrorSuite = unittest.TestLoader().loadTestsFromTestCase(JamDeleteErrorTests)
    jamPlayErrorSuite = unittest.TestLoader().loadTestsFromTestCase(JamPlayErrorTests)
    
    allSuites = unittest.TestSuite([jamSimpleSuite, jamDownloadErrorSuite, jamDeleteErrorSuite, jamPlayErrorSuite])
    unittest.TextTestRunner(verbosity=2).run(allSuites)
