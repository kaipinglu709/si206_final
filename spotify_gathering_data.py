import requests
import sqlite3
import base64
import os

# Configuration
CLIENT_ID = '67285455157c4514a30970aee1cb0331'
CLIENT_SECRET = '2d75abacd62f4139aed9780b61078c5b'
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
BASE_URL = 'https://api.spotify.com/v1/'

def authenticate_spotify():
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    response = requests.post(token_url, headers=headers, data=data)
    return response.json().get('access_token') if response.status_code == 200 else None

def get_featured_playlists(access_token):
    featured_playlists_url = f'{BASE_URL}browse/featured-playlists'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(featured_playlists_url, headers=headers)
    if response.status_code == 200:
        return response.json()['playlists']['items']
    else:
        print(f"Error fetching playlists: {response.json().get('error', {}).get('message', '')}")
        return []

def get_playlist_tracks(access_token, playlist_id):
    playlist_tracks_url = f"{BASE_URL}playlists/{playlist_id}/tracks"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(playlist_tracks_url, headers=headers)
    if response.status_code == 200:
        return [track['track'] for track in response.json()['items'] if track.get('track')]
    else:
        print(f"Failed to retrieve tracks for playlist {playlist_id}. Status code: {response.status_code}")
        return []

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS playlists (id TEXT PRIMARY KEY, name TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS tracks (id TEXT PRIMARY KEY, name TEXT, artist TEXT, playlist_id TEXT, FOREIGN KEY(playlist_id) REFERENCES playlists(id));")
    conn.commit()
    conn.close()

def insert_data(access_token):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    playlists = get_featured_playlists(access_token)
    for playlist in playlists:
        c.execute('INSERT OR IGNORE INTO playlists (id, name) VALUES (?, ?)', (playlist['id'], playlist['name']))
        tracks = get_playlist_tracks(access_token, playlist['id'])
        for track in tracks:
            c.execute('INSERT OR IGNORE INTO tracks (id, name, artist, playlist_id) VALUES (?, ?, ?, ?)',
                      (track['id'], track['name'], track['artists'][0]['name'] if track['artists'] else "Unknown", playlist['id']))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database()
    access_token = authenticate_spotify()
    if access_token:
        insert_data(access_token)
    else:
        print("Failed to authenticate with Spotify")
