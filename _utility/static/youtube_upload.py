#!/usr/bin/env python3
"""Upload a video to YouTube (private) using saved OAuth2 token, optionally adding to a playlist."""
import argparse, json, os, sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN = os.path.expanduser(
    "~/.openclaw/workspace/projects/myJob/PERSONALE/personale_tempo_libero/intv recording/youtube_token.json"
)
PLAYLIST_CACHE = os.path.expanduser(
    "~/.openclaw/workspace/projects/myJob/PERSONALE/personale_tempo_libero/intv recording/youtube_playlists.json"
)

def get_creds():
    t = json.load(open(TOKEN))
    creds = Credentials(
        token=t["token"],
        refresh_token=t["refresh_token"],
        token_uri=t["token_uri"],
        client_id=t["client_id"],
        client_secret=t["client_secret"],
        scopes=t["scopes"],
    )
    if not creds.valid:
        creds.refresh(Request())
        t["token"] = creds.token
        json.dump(t, open(TOKEN, "w"), indent=2)
    return creds

def get_or_create_playlist(yt, name, privacy="private"):
    cache = {}
    if os.path.exists(PLAYLIST_CACHE):
        cache = json.load(open(PLAYLIST_CACHE))
    if name in cache:
        return cache[name]
    resp = yt.playlists().list(part="snippet", mine=True, maxResults=50).execute()
    for item in resp.get("items", []):
        if item["snippet"]["title"].lower() == name.lower():
            pid = item["id"]
            cache[name] = pid
            json.dump(cache, open(PLAYLIST_CACHE, "w"), indent=2)
            print(f"Playlist esistente: '{name}' ({pid})")
            return pid
    pl = yt.playlists().insert(
        part="snippet,status",
        body={"snippet": {"title": name}, "status": {"privacyStatus": privacy}},
    ).execute()
    pid = pl["id"]
    cache[name] = pid
    json.dump(cache, open(PLAYLIST_CACHE, "w"), indent=2)
    print(f"Playlist creata: '{name}' ({pid})")
    return pid

def add_to_playlist(yt, video_id, playlist_id):
    yt.playlistItems().insert(
        part="snippet",
        body={"snippet": {"playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": video_id}}},
    ).execute()
    print(f"Aggiunto a playlist ({playlist_id})")

def upload(file_path, title, description="", privacy="private", playlist=None):
    creds = get_creds()
    yt = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {"title": title, "description": description, "categoryId": "17"},
        "status": {"privacyStatus": privacy},
    }
    media = MediaFileUpload(file_path, mimetype="video/MP2T", chunksize=10*1024*1024, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    print(f"Upload: {file_path} → '{title}' [{privacy}]")
    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            print(f"  {int(status.progress()*100)}%", end="\r")
    video_id = response["id"]
    print(f"\nDone! Video ID: {video_id}")
    print(f"URL: https://www.youtube.com/watch?v={video_id}")
    if playlist:
        pid = get_or_create_playlist(yt, playlist)
        add_to_playlist(yt, video_id, pid)
    return video_id

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("title")
    p.add_argument("--description", default="")
    p.add_argument("--privacy", default="private", choices=["private","unlisted","public"])
    p.add_argument("--playlist", default=None, help="Nome playlist YouTube (creata se non esiste)")
    args = p.parse_args()
    upload(args.file, args.title, args.description, args.privacy, args.playlist)
