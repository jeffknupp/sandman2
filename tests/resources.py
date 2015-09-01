TRACK_ONE = {
    'TrackId': 1,
    'UnitPrice': 0.99,
    'Composer': 'Angus Young, Malcolm Young, Brian Johnson',
    'Bytes': 11170334,
    'GenreId': 1,
    'Name': 'For Those About To Rock (We Salute You)',
    'Milliseconds': 343719,
    'AlbumId': 1,
    'MediaTypeId': 1,
}

RESOURCE_ETAGS = (
    '"8a4a9037a1eb0a50ed7f8d523e05cfcb"',
    '"7bcefa90a6faacf8460b00f0bb217388"',
)

COLLECTION_ETAGS = (
    '"edbada3ecdab228917e6829981313e06"',
    '"92bb34e18945a21a42a5a92204996576"',
)


NEW_ARTIST = {
    'Name': 'Jeff Knupp',
    'ArtistId': 276,
}

REPLACED_ARTIST = {
    'Name': 'Metallica',
    'ArtistId': 1,
}

NEW_ALBUM = {
    'AlbumId': 348,
    'ArtistId': 1,
    'Title': 'Some Title',
}

ARTIST_META = {
    "ArtistId": "INTEGER (required)",
    "Name": "NVARCHAR(120)",
}

GET_ERROR_MESSAGE = 'Not allowed to call GET on collection'

INVALID_ACTION_MESSAGE = 'Invalid action'
