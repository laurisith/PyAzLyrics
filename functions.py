import os, sys
from urllib.request import urlopen
from bs4 import BeautifulSoup


class Artist(object):
    def __init__(self, name):
        self.name = name

    def getAlbums(self):
        return PyAZLyrics.getAlbums(self.name)

    def artist(self):
        return self.name


class Album(object):
    def __init__(self, name, artist):
        self.name = name.lower().strip()
        self.artist = artist.lower().strip()
        self.tracks = []

    def artist(self):
        return self.artist

    def tracks(self):
        return self.tracks

    def add_track(self, track):
        self.tracks.append(track)


class Track(object):
    def __init__(self, trackname, album, artist, href, tracknumber):
        self.name = trackname.lower().strip()
        self.album = album.lower().strip()
        self.artist = artist.lower().strip()
        self.href = href
        self.number = tracknumber

    def name(self):
        return self.name

    def album(self):
        return self.album

    def artist(self):
        return self.artist

    def href(self):
        return self.href

    def number(self):
        return self.number

    def getLyrics(self):
        return PyAZLyrics.getLyricsForSongHref(self.href)


class PyAZLyrics:
    @staticmethod
    def getArtistSoap(artist):
        artist_query = "+".join(artist.lower().strip().split(" "))
        artist_query_page_url = urlopen(
            'https://search.azlyrics.com/search.php?q=' + artist_query)
        soap = BeautifulSoup(artist_query_page_url.read(), 'html.parser')

        panels = soap.select('div .panel')
        for panel in panels:
            panel_head = panel.select('.panel-heading')
            if 'Artist results' in panel_head[0].getText():
                artist_href = panel.select('table td a')
                if len(artist_href) > 1:
                    return 'TooManyArtists'
                elif len(artist_href) == 1:
                    artist_url = urlopen(artist_href[0]['href'])
                    soap_artist = BeautifulSoup(artist_url.read(),
                                                'html.parser')
                    return soap_artist
                else:
                    return 'NoArtist'
        return 'NoArtist'

    @staticmethod
    def getLyricsForSongHref(song_href):
        if 'https://www.azlyrics.com/lyrics/' in song_href:
            song_url = urlopen(song_href)
            soap = BeautifulSoup(song_url.read(), 'html.parser')

            song_lyrics = soap.find_all('div', attrs={'class': None,
                                                      'id': None})
            return song_lyrics[0].getText()
        else:
            return 'NoLyrics'

    @staticmethod
    def getLyricsSingleSimple(artist, song):
        albums = Artist(artist).getAlbums()
        if albums == 'NoAlbums':
            return 'NoLyrics'
        else:
            song = song.lower().strip()
            for album in albums:
                for track in album.tracks:
                    if track.name in song:
                        return track.getLyrics()
            return 'NoLyrics'

    @staticmethod
    def getLyricsSingleComplex(artist, album_name, song, tracknumber):
        albums = Artist(artist).getAlbums()
        if albums == 'NoAlbums':
            return 'NoLyrics'
        else:
            song = song.lower().strip()
            album_name = album_name.lower().strip()
            for album in albums:
                for track in album.tracks:
                    if track.name in song or \
                            (track.album in album_name and tracknumber == track.number):
                        return track.getLyrics()
            return 'NoLyrics'

    @staticmethod
    def getLyricsMultiSimple(albums, song):
        if albums == 'NoAlbums':
            return 'NoLyrics'
        else:
            song = song.lower().strip()
            for album in albums:
                for track in album.tracks:
                    if track.name in song:
                        return track.getLyrics()
            return 'NoLyrics'

    @staticmethod
    def getLyricsMultiComplex(albums, album_name, song, tracknumber):
        if albums == 'NoAlbums':
            return 'NoLyrics'
        else:
            song = song.lower().strip()
            album_name = album_name.lower().strip()
            for album in albums:
                for track in album.tracks:
                    if track.name in song or\
                            (track.album in album_name and tracknumber == track.number):
                        return track.getLyrics()
            return 'NoLyrics'

    @staticmethod
    def getAlbums(artist):
        root_href = "https://www.azlyrics.com"
        artist = artist.lower().strip().encode('ascii', 'replace').decode('ascii')

        if PyAZLyrics.getArtistSoap(artist) == 'NoArtist' or \
                PyAZLyrics.getArtistSoap(artist) == 'TooManyArtists':
            return 'NoAlbums'
        else:
            soap = PyAZLyrics.getArtistSoap(artist).select('div#listAlbum div')

            albums = []
            album_name = ''

            for item in soap:
                if item.has_attr('class'):
                    if item['class'][0] == 'album':
                        album_name = item.select('b')[0].getText().lower().replace('\"', '').strip()
                        albums.append(Album(album_name, artist))
                    if item['class'][0] == 'listalbum-item':
                        track_name = item.getText().lower().strip()
                        track_href = root_href + item.select('a')[0]['href'][2:]
                        track_number = len(albums[-1].tracks) + 1

                        track = Track(track_name, album_name, artist,
                                      track_href, track_number)
                        albums[-1].add_track(track)

            return albums

def main():
    artist = 'öööööööö'
    song = 'Overkill'
    print(PyAZLyrics.getLyricsSingleSimple(artist, song))


if __name__ == '__main__':
    main()
