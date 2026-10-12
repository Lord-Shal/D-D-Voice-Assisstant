import json
import os
import random
import sys
from dotenv import load_dotenv  
load_dotenv() 

 
import spotipy                                   
from spotipy.oauth2 import SpotifyOAuth          
 
from src.speech.intent_detector import VALID_MOODS   
 
TAGS_FILE = "mood_tags.json"                     
SCOPE = "user-modify-playback-state user-read-playback-state playlist-read-private"
 
 
class SpotifyPlayerError(Exception):             
    pass
 
 
class SpotifyMoodPlayer:
    def __init__(self, tags_file=TAGS_FILE, load_tags=True):
        playlist_id = os.environ.get("SPOTIPY_PLAYLIST_ID")
        if not playlist_id:
            raise SpotifyPlayerError("SPOTIPY_PLAYLIST_ID environment variable not set")
 
        self.playlist_id = playlist_id
        self.tags_file = tags_file
 
        try:
            
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE))
            
            self.sp.devices()
        except Exception as error:
            raise SpotifyPlayerError(f"Could not connect to Spotify: {error}") from error
 
        self.mood_index = {}                     
        if load_tags:
            self.mood_index = self._build_mood_index()
            self._warn_about_tags()
 
    # ---------- Tag handling ----------
    def _fetch_playlist_tracks(self):
        """Return a list of {'uri', 'name'} for every track in the playlist."""
        tracks = []
        try:
            results = self.sp.playlist_items(self.playlist_id, limit=100)  
            while results:
                for entry in results["items"]:
                    
                    t = entry.get("track") or entry.get("item")
                    if t and t.get("uri"):                      
                        artist = t["artists"][0]["name"] if t.get("artists") else ""
                        tracks.append({"uri": t["uri"], "name": f"{t['name']} - {artist}"})
                results = self.sp.next(results) if results.get("next") else None 
        except Exception as error:
            raise SpotifyPlayerError(f"Could not read playlist: {error}") from error
        return tracks
 
    def export_tag_template(self):
        """Write mood_tags.json with every track and an empty moods list to fill in."""
        template = [{"uri": t["uri"], "name": t["name"], "moods": []}
                    for t in self._fetch_playlist_tracks()]
        with open(self.tags_file, "w", encoding="utf-8") as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        print(f"Wrote {len(template)} tracks to {self.tags_file}.")
        print(f"Fill in moods for each track using: {', '.join(VALID_MOODS)}")
 
    def _build_mood_index(self):
        """Read the tag file and return {mood: [track uris]}."""
        if not os.path.exists(self.tags_file):
            raise SpotifyPlayerError(
                f"{self.tags_file} not found. Run: python -m src.apps.spotify_player --export-tags")
        try:
            with open(self.tags_file, encoding="utf-8") as f:
                tagged = json.load(f)
        except json.JSONDecodeError as error:
            raise SpotifyPlayerError(f"{self.tags_file} is not valid JSON: {error}") from error
 
        index = {}
        for track in tagged:
            for mood in track.get("moods", []):
                index.setdefault(mood.lower(), []).append(track["uri"]) 
        return index
 
    def _warn_about_tags(self):
        """Warn if the tag file and VALID_MOODS don't line up (typos, empty moods)."""
        for mood in VALID_MOODS:               
            if mood not in self.mood_index:      
                print(f"[warning] no tracks tagged '{mood}', that cue will be ignored")
        for mood in self.mood_index:            
            if mood not in VALID_MOODS:          
                print(f"[warning] tag '{mood}' is not in VALID_MOODS (typo?)")
 
    # ---------- Playback ----------
    def _get_device_id(self):
        """Find the Spotify desktop app on this PC (prefers the active device)."""
        devices = self.sp.devices()["devices"]
        if not devices:
            return None                          
        for d in devices:
            if d["is_active"]:
                return d["id"]
        return devices[0]["id"]                 
 
    def play_mood(self, mood):
        """Start playing tracks tagged with this mood. Returns True if playback started."""
        uris = list(self.mood_index.get(mood.lower(), []))
        if not uris:
            print(f"No tracks tagged '{mood}', keeping current music.")
            return False
 
        try:
            device_id = self._get_device_id()
            if device_id is None:
                print("No Spotify device found. Open the Spotify app on your PC.")
                return False
 
            random.shuffle(uris)                 
            self.sp.start_playback(device_id=device_id, uris=uris[:100])
        except spotipy.SpotifyException as error:
            print(f"Spotify playback error: {error}")   
            return False
        return True
 
 
if __name__ == "__main__":
    if "--export-tags" in sys.argv:
        SpotifyMoodPlayer(load_tags=False).export_tag_template()
    else:
        print("Usage: python -m src.apps.spotify_player --export-tags")