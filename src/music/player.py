"""Local soundtrack playback for the D&D voice assistant."""
from pathlib import Path
import random

import pygame


class MusicPlaybackError(Exception):
    pass


class MusicPlayer:
    # Gemini mood -> actual folder in assets/music
    MOOD_FOLDERS = {
        "boss": "boss",
        "combat": "combat",
        "spooky": "spooky",
        "sad": "sad",
        "tension": "tension",
        "exploration": "travel",
    }

    def __init__(self, music_root=None, volume=0.4):
        # player.py is <project>/src/music/player.py
        self.music_root = (Path(music_root) if music_root else
                           Path(__file__).resolve().parents[2] / "assets" / "music")
        self.current_mood = None
        self.current_track = None
        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
        except pygame.error as exc:
            raise MusicPlaybackError(f"Could not initialise audio output: {exc}") from exc

    def play_mood(self, mood):
        """Return True if a track is playing for this mood; False if unavailable."""
        if mood == self.current_mood and pygame.mixer.music.get_busy():
            return True

        folder_name = self.MOOD_FOLDERS.get(mood)
        if folder_name is None:
            print(f"[Music] No folder mapped for '{mood}'; keeping current music.")
            return False

        folder = self.music_root / folder_name
        tracks = sorted(folder.glob("*.mp3")) if folder.is_dir() else []
        if not tracks:
            print(f"[Music] No MP3s found in {folder}; keeping current music.")
            return False

        # Avoid an immediate repeat if there are multiple choices.
        choices = [track for track in tracks if track != self.current_track]
        track = random.choice(choices or tracks)
        try:
            pygame.mixer.music.load(str(track))
            pygame.mixer.music.play(loops=-1, fade_ms=750)
        except (pygame.error, OSError) as exc:
            raise MusicPlaybackError(f"Cannot play {track.name}: {exc}") from exc

        self.current_mood = mood
        self.current_track = track
        print(f"[Music] Now playing: {track.name} (mood: {mood})")
        return True

    def stop(self):
        pygame.mixer.music.stop()
        self.current_mood = None
        self.current_track = None

    def close(self):
        self.stop()
        pygame.mixer.quit()
