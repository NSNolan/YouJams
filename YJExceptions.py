##
# Playlist Exceptions
##

class PlaylistError(Exception):
    """unused"""
    pass

# Playlist Add Exceptions

class PlaylistAddError(PlaylistError):
    """unused"""
    pass

class PlaylistAddFailureError(PlaylistAddError):
    pass

# Playlist Remove Exceptions

class PlaylistRemoveError(PlaylistError):
    """unused"""
    pass

class PlaylistRemoveNoJamPlayForUUIDError(PlaylistRemoveError):
    pass

class PlaylistRemoveNoJamForTokenError(PlaylistRemoveError):
    pass

class PlaylistRemoveFailureError(PlaylistRemoveError):
    pass

##
# Jam Exceptions
##

class JamError(Exception):
    """unused"""
    pass

class JamUnknownStateError(JamError):
    pass

# Jam Download Exceptions

class JamDownloadError(JamError):
    """unused"""
    pass

class JamDownloadNoJamDirectoryError(JamDownloadError):
    pass

class JamDownloadIsDeletingError(JamDownloadError):
    pass

class JamDownloadFailureError(JamDownloadError):
    pass

# Jam Delete Exceptions

class JamDeleteError(JamError):
    """unused"""
    pass

class JamDeleteNotDownloadedError(JamDeleteError):
    pass

class JamDeleteOnlyReferenceIsDownloadingError(JamDeleteError):
    pass

class JamDeleteOnlyReferenceIsPlayingError(JamDeleteError):
    pass

class JamDeleteOnlyReferenceIsDeletingError(JamDeleteError):
    pass

class JamDeleteFailureError(JamDeleteError):
    pass

# Jam Play Exceptions

class JamPlayError(JamError):
    """unused"""
    pass

class JamPlayNotDownloadedError(JamPlayError):
    pass

class JamPlayIsDownloadingError(JamPlayError):
    pass

class JamPlayIsPlayingError(JamPlayError):
    pass

class JamPlayIsDeletingError(JamPlayError):
    pass

class JamPlayFailureError(JamPlayError):
    pass
