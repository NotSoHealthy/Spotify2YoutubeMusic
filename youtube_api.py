import os
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from copy_playlists import *
import yt_dlp
from dotenv import load_dotenv
load_dotenv()

client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

# Scopes define the access level
SCOPES = ["https://www.googleapis.com/auth/youtube"]
TOKEN_FILE = "token.json"

def save_credentials_to_file(creds):
    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())

def load_credentials_from_file():
    with open(TOKEN_FILE, "r") as token:
        creds_data = token.read()
        return Credentials.from_authorized_user_info(json.loads(creds_data), SCOPES)
    
def delete_credentials_file():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        print(f"Deleted credentials file: {TOKEN_FILE}")
    else:
        print(f"No credentials file found at: {TOKEN_FILE}")

def authenticate():
    creds = None
    # Load saved credentials if they exist
    if os.path.exists(TOKEN_FILE):
        creds = load_credentials_from_file()

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config({
            "installed": {
                "client_id": client_id,
                "project_id": "spotify2youtubemusic-461317",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": client_secret,
                "redirect_uris": ["http://localhost"]
            }}, SCOPES)
            creds = flow.run_local_server(
                port=8234,
                access_type='offline',
                prompt='consent'
            )
        save_credentials_to_file(creds)

def is_authnenticated():
    if os.path.exists(TOKEN_FILE):
        creds = load_credentials_from_file()
        return creds and creds.valid
    else:
        return False

def get_playlists(youtube):
    next_page_token = None
    playlists = []

    while True:
        request = youtube.playlists().list(
            part="id,snippet,contentDetails",
            mine=True,
            pageToken=next_page_token,
            maxResults=50
        )
        response = request.execute()

        for playlist in response.get("items", []):
            # print(f"{playlist['snippet']['title']} ({playlist['id']})")
            playlists.append(playlist)

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return playlists
    
def get_videos_in_playlist(youtube, playlist_id):
    video_ids = []
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part="id,snippet,contentDetails",
            maxResults=50,
            pageToken=next_page_token,
            playlistId=playlist_id,
        )
        response = request.execute()

        for item in response.get("items", []):
            # title = item["snippet"]["title"]
            # video_id = item["snippet"]["resourceId"]["videoId"]
            # print(f"{title}: https://www.youtube.com/watch?v={video_id}")
            video_ids.append(item)

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    
    return video_ids

def add_videos_to_playlist(youtube, playlist_id, videos):
    playlist_contents = get_videos_in_playlist(youtube, playlist_id)
    for video in videos:
        if video not in playlist_contents:
            request = youtube.playlistItems().insert(
                part='snippet',
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "position": 0,
                        "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video
                        }
                    }
                }
            )
            response = request.execute()
            print(response)

def create_playlist(youtube, playlist_name):
    request = youtube.playlists().insert(
        part='snippet',
        body={
            'snippet': {
                'title': playlist_name,
            }
        }
    )

    response = request.execute()
    
def find_song(track_query):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': 'in_playlist',
    }

    search_query = f"ytsearch{1}:{track_query}"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=False)
        if 'entries' in info and info['entries']:
            return info['entries'][0].get('id')
        else:
            return None
        
def delete_playlist(youtube, playlist_id):
    request = youtube.playlists().delete(
        id=playlist_id
    )
    print(request.execute())


def load():
    creds = None
    authenticate() 
    creds = load_credentials_from_file()
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)
    return youtube

def main():
    youtube = load()
    print(delete_playlist())
    # print(get_playlists(youtube))
    # get_videos_in_playlist(youtube, 'PLMMjwcqXrl7m2VJgo6leEqtVLKooY6qSz')
    # create_playlist(youtube, 'test')
    # add_videos_to_playlist(youtube, 'PLMMjwcqXrl7krKY4YuVViNGFW8R0l5xRh', ['EyR2-C9ggi0'])

    # print(get_spotify_playlist_tracks('16z2QPMjE5Kpc1tcHoWbRQ'))
    # print(search_track_on_ytm('Lady Gaga - Just Dance'))

if __name__ == "__main__":
    main()