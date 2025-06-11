import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyClient:
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_url = 'http://127.0.0.1:8888/callback'
        self.scopes = "playlist-read-private playlist-read-collaborative user-library-read user-follow-read"
        self.cache_path = (
            os.getenv('APPDATA') + '\\spotify2youtubemusic\\spotify.cache'
            if os.name == 'nt'
            else os.path.expanduser('~/.cache') + '/spotify2youtubemusic/spotify.cache'
        )
        cache_dir = os.path.dirname(self.cache_path)
        os.makedirs(cache_dir, exist_ok=True)
        self.sp = self.authenticate()

    def authenticate(self):
        """Authenticate with Spotify and return the authenticated client."""
        return spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_url,
            scope=self.scopes,
            cache_path=self.cache_path,
            show_dialog=True,
        ))

    def get_all_playlists(self):
        playlists = []
        results = self.sp.current_user_playlists()
        while results:
            playlists.extend(results['items'])
            if results['next']:
                results = self.sp.next(results)
            else:
                results = None
        return playlists
    
    def get_all_followed_artists(self):
        artists = []
        results = self.sp.current_user_followed_artists()
        while results:
            artists.extend(results['items'])
            if results['next']:
                results = self.sp.next(results)
            else:
                results = None
        return artists

    def get_all_playlist_songs(self, playlist_id):
        songs = []
        results = self.sp.playlist_items(playlist_id=playlist_id)
        while results:
            songs.extend(results['items'])
            if results['next']:
                results = self.sp.next(results)
            else:
                results = None
        return songs

if __name__ == "__main__":
    spotify_client = SpotifyClient()
    print(spotify_client.get_all_playlists())