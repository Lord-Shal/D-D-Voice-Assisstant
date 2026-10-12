import json, time
from dotenv import load_dotenv
load_dotenv()

from src.apps.spotify_player import SpotifyMoodPlayer

player = SpotifyMoodPlayer(load_tags=False)    # skip the tag index, we only need the login

print("Devices:", player.sp.devices())         # shows is_active / is_restricted per device

uri = json.load(open("mood_tags.json"))[0]["uri"]    # first track in your tag file
print("Testing:", uri)

player.sp.start_playback(device_id=player._get_device_id(), uris=[uri])
time.sleep(3)                                  # give Spotify a moment to start the track
print("Now playing:", player.sp.current_playback())