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
    '"8527642c9c0fbbd6807e49c30d93a2c6"',
    '"d7078e022cb3398329a4254468c80fad"',
)

COLLECTION_ETAGS = (
    # Original ETags
    '"4368a846206ec071cb251951b958c2a0"',
    '"f8d044bc2810a3758722557101e1f4a2"',
    '"8527642c9c0fbbd6807e49c30d93a2c6"',
    '"90f8a11222df8b83d6f1cee626a154a5"',
    '"c59f5215ea673b399145eccfcbb3e89c"',
    '"207ab6c6190915dbde0cba288e5ce35d"',
    # Updated ETags (Since the collection is no longer nested under resources)
    '"4042d59977793af77f719c75ca36e2e3"',
)


NEW_ARTIST = {
    'Name': 'Jeff Knupp',
    'ArtistId': 277,
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
    "Name": "NVARCHAR(120)"
}

GET_ERROR_MESSAGE = 'Not allowed to call GET on collection'

INVALID_ACTION_MESSAGE = 'Invalid action'
