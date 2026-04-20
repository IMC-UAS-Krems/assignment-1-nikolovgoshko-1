from datetime import timedelta
from streaming.tracks import Song
from streaming.users import PremiumUser, FamilyMember
from streaming.playlists import CollaborativePlaylist


class StreamingPlatform:
    def __init__(self, name):
        self.name = name
        self.catalogue = {}
        self._users = {}
        self._artists = {}
        self._albums = {}
        self._playlists = {}
        self._sessions = []

    def add_track(self, track):
        self.catalogue[track.track_id] = track

    def add_user(self, user):
        self._users[user.user_id] = user

    def add_artist(self, artist):
        self._artists[artist.artist_id] = artist

    def add_album(self, album):
        self._albums[album.album_id] = album

    def add_playlist(self, playlist):
        self._playlists[playlist.playlist_id] = playlist

    def record_session(self, session):
        self._sessions.append(session)
        session.user.add_session(session)

    def get_track(self, track_id):
        return self.catalogue.get(track_id)

    def get_user(self, user_id):
        return self._users.get(user_id)

    def get_artist(self, artist_id):
        return self._artists.get(artist_id)

    def get_album(self, album_id):
        return self._albums.get(album_id)

    def all_users(self):
        return list(self._users.values())

    def all_tracks(self):
        return list(self.catalogue.values())

    def total_listening_time_minutes(self, start, end):
        total = 0
        for session in self._sessions:
            if start <= session.timestamp <= end:
                total += session.duration_listened_seconds
        return total / 60

    def avg_unique_tracks_per_premium_user(self, days=30):
        premium_users = []
        for user in self._users.values():
            if isinstance(user, PremiumUser):
                premium_users.append(user)

        if len(premium_users) == 0:
            return 0.0

        latest = None
        for session in self._sessions:
            if latest is None or session.timestamp > latest:
                latest = session.timestamp

        if latest is None:
            return 0.0

        start_time = latest - timedelta(days=days)

        total_unique = 0
        for user in premium_users:
            unique_tracks = set()
            for session in user.sessions:
                if start_time <= session.timestamp <= latest:
                    unique_tracks.add(session.track.track_id)
            total_unique += len(unique_tracks)

        return total_unique / len(premium_users)

    def track_with_most_distinct_listeners(self):
        if len(self._sessions) == 0:
            return None

        listeners_per_track = {}

        for session in self._sessions:
            track = session.track
            user = session.user

            if track.track_id not in listeners_per_track:
                listeners_per_track[track.track_id] = set()

            listeners_per_track[track.track_id].add(user.user_id)

        best_track = None
        best_count = -1

        for track_id, listeners in listeners_per_track.items():
            if len(listeners) > best_count:
                best_count = len(listeners)
                best_track = self.get_track(track_id)

        return best_track

    def avg_session_duration_by_user_type(self):
        grouped = {}

        for session in self._sessions:
            type_name = type(session.user).__name__

            if type_name not in grouped:
                grouped[type_name] = []

            grouped[type_name].append(session.duration_listened_seconds)

        result = []

        for type_name, durations in grouped.items():
            avg = sum(durations) / len(durations)
            result.append((type_name, avg))

        result.sort(key=lambda x: x[1], reverse=True)
        return result

    def total_listening_time_underage_sub_users_minutes(self, age_threshold=18):
        total = 0

        for session in self._sessions:
            if isinstance(session.user, FamilyMember) and session.user.age < age_threshold:
                total += session.duration_listened_seconds

        return total / 60

    def top_artists_by_listening_time(self, n=5):
        artist_totals = {}

        for session in self._sessions:
            track = session.track

            if isinstance(track, Song):
                artist = track.artist

                if artist.artist_id not in artist_totals:
                    artist_totals[artist.artist_id] = 0

                artist_totals[artist.artist_id] += session.duration_listened_seconds

        result = []

        for artist_id, total_seconds in artist_totals.items():
            artist = self.get_artist(artist_id)
            result.append((artist, total_seconds / 60))

        result.sort(key=lambda x: x[1], reverse=True)
        return result[:n]

    def user_top_genre(self, user_id):
        user = self.get_user(user_id)

        if user is None:
            return None

        if len(user.sessions) == 0:
            return None

        genre_totals = {}
        total = 0

        for session in user.sessions:
            genre = session.track.genre

            if genre not in genre_totals:
                genre_totals[genre] = 0

            genre_totals[genre] += session.duration_listened_seconds
            total += session.duration_listened_seconds

        if not genre_totals:
            return None

        best_genre = max(genre_totals, key=genre_totals.get)  # type: ignore
        percentage = (genre_totals[best_genre] / total) * 100

        return (best_genre, percentage)

    def collaborative_playlists_with_many_artists(self, threshold=3):
        result = []

        for playlist in self._playlists.values():
            if isinstance(playlist, CollaborativePlaylist):
                artists = set()

                for track in playlist.tracks:
                    if isinstance(track, Song):
                        artists.add(track.artist.artist_id)

                if len(artists) > threshold:
                    result.append(playlist)

        return result

    def avg_tracks_per_playlist_type(self):
        normal_counts = []
        collab_counts = []

        for playlist in self._playlists.values():
            if type(playlist).__name__ == "Playlist":
                normal_counts.append(len(playlist.tracks))
            elif isinstance(playlist, CollaborativePlaylist):
                collab_counts.append(len(playlist.tracks))

        result = {}

        if len(normal_counts) == 0:
            result["Playlist"] = 0.0
        else:
            result["Playlist"] = sum(normal_counts) / len(normal_counts)

        if len(collab_counts) == 0:
            result["CollaborativePlaylist"] = 0.0
        else:
            result["CollaborativePlaylist"] = sum(
                collab_counts) / len(collab_counts)

        return result

    def users_who_completed_albums(self):
        result = []

        for user in self._users.values():
            completed = []

            listened_track_ids = set()
            for session in user.sessions:
                listened_track_ids.add(session.track.track_id)

            for album in self._albums.values():
                if len(album.tracks) == 0:
                    continue

                album_track_ids = set()
                for track in album.tracks:
                    album_track_ids.add(track.track_id)

                if album_track_ids.issubset(listened_track_ids):
                    completed.append(album.title)

            if len(completed) > 0:
                result.append((user, completed))

        return result
