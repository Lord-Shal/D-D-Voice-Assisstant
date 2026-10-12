import json
import time
 
from dotenv import load_dotenv
load_dotenv()                                     # read .env (API keys, playlist ID)
 
from src.apps.spotify_player import SpotifyMoodPlayer
 
player = SpotifyMoodPlayer(load_tags=False)       # log in, skip the tag index
sp = player.sp
 
with open("mood_tags.json", encoding="utf-8") as f:
    tracks = json.load(f)[:3]                     # first three tracks in your tag file
 
for device in sp.devices()["devices"]:            # try every player Spotify can see
    print(f"\n=== {device['name']} ===")
    for track in tracks:
        try:
            sp.start_playback(device_id=device["id"], uris=[track["uri"]])
        except Exception as error:
            print(f"  {track['name']}: ERROR {error}")
            continue
 
        time.sleep(5)                             # give the player time to load the track
        state = sp.current_playback()
        playing = bool(state and state.get("is_playing"))
        print(f"  {track['name']}: is_playing={playing}")
 
        if playing:                               # stop it so the test isn't loud
            try:
                sp.pause_playback(device_id=device["id"])
            except Exception:
                pass