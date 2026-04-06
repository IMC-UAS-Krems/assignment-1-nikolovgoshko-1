class Track:
    def __init__(self, track_id, title, duration_seconds, genre):
        self.track_id = track_id
        self.title = title
        self.duration_seconds = duration_seconds
        self.genre = genre

    def duration_minutes(self):
        return self.duration_seconds / 60

    def __str__(self):
        return self.title


class Song(Track):
    def __init__(self, track_id, title, duration_seconds, genre, artist):
        Track.__init__(self, track_id, title, duration_seconds, genre)
        self.artist = artist

        if self.artist is not None:
            self.artist.add_track(self)


class SingleRelease(Song):
    def __init__(self, track_id, title, duration_seconds, genre, artist, release_date):
        Song.__init__(self, track_id, title, duration_seconds, genre, artist)
        self.release_date = release_date


class AlbumTrack(Song):
    def __init__(self, track_id, title, duration_seconds, genre, artist, track_number, album=None):
        Song.__init__(self, track_id, title, duration_seconds, genre, artist)
        self.track_number = track_number
        self.album = album


class Podcast(Track):
    def __init__(self, track_id, title, duration_seconds, genre, host, description):
        Track.__init__(self, track_id, title, duration_seconds, genre)
        self.host = host
        self.description = description


class InterviewEpisode(Podcast):
    def __init__(self, track_id, title, duration_seconds, genre, host, description, guest):
        Podcast.__init__(self, track_id, title,
                         duration_seconds, genre, host, description)
        self.guest = guest


class NarrativeEpisode(Podcast):
    def __init__(self, track_id, title, duration_seconds, genre, host, description, season, episode_number):
        Podcast.__init__(self, track_id, title,
                         duration_seconds, genre, host, description)
        self.season = season
        self.episode_number = episode_number


class AudiobookTrack(Track):
    def __init__(self, track_id, title, duration_seconds, genre, author, narrator):
        Track.__init__(self, track_id, title, duration_seconds, genre)
        self.author = author
        self.narrator = narrator
