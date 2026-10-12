import json # passing model response
import time # time stamp transcript to remove old ones from buffer
import os # read env vars
from dataclasses import dataclass # for MusicCUe
from typing import Optional # 

import google.generativeai as genai

class IntentDetectionError(Exception): #tried following same pattern for recording and transcribing
    pass

@dataclass
class MusicCue:
    cue_detected: bool
    mood:Optional[str] = None # optional is cool its like suggesting there is a string or none. 
    confidence: float = 0.0
    raw_reasoning: Optional[str] = None



CANDIDATE_MOODS =["exploration", "tavern", "tension", "victory", "adventure", "boss", "sad", "morning", "spooky", "city", "night", "windy", "sunrise", "scary", "whimsical", "circus", "cozy", "war", "family", "sorrow", "hope","despair", "anger", "frustration"] #extend list to match spotify playlist
TAGS_FILE = "mood_tags.json" 
 

def load_valid_moods(tags_file=TAGS_FILE):
    """Return the moods that actually appear in the tag file."""
    try:
        with open(tags_file, encoding="utf-8") as f:
            tagged = json.load(f)
    except (OSError, json.JSONDecodeError):          
        return list(CANDIDATE_MOODS)                
    moods = sorted({m.lower() for t in tagged for m in t.get("moods", [])})
    return moods or list(CANDIDATE_MOODS)            

VALID_MOODS = load_valid_moods()

SYSTEM_PROMPT = f"""You are monitoring a live transcript of a Dungeons & Dragons session.
Your only job is to detect when the Dungeon Master's speech implies background music should
change, and if so, which mood best fits.
 
Valid moods: {", ".join(VALID_MOODS)}
 
Respond ONLY with JSON, no preamble, no markdown fences, in this exact shape:
{{"cue_detected": true/false, "mood": "<one of the valid moods or null>", "confidence": 0.0-1.0, "reasoning": "<one short sentence>"}}
 
Only set cue_detected to true if the DM is clearly narrating a scene change or moment that
would benefit from a music shift (e.g. combat starting, entering a tavern, a tense standoff,
a victory). Ordinary dialogue, rules discussion, or out-of-character chat should be false. 
"""
class MusicIntentDetector:
    def __init__(self, model="gemini-3.1-flash-lite", buffer_window_seconds=30,# check last 30. Im just guessing this ibr 
                 min_check_interval_seconds=10): # won't go to api key more than once every 10 seconds. Im just guessing this ibr 
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise IntentDetectionError("GEMINI_API_KEY environment variable no set")

        try:
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(
                model_name=model,
                system_instruction = SYSTEM_PROMPT,
                generation_config= {"response_mime_type": "application/json"}, # forces JSON output. Prompt mimght not be needed. creates structured data
            )
        except Exception as error:
            raise IntentDetectionError(f"Could not initialise client:{error}") from error

        self.model = model
        self.buffer_window_seconds = buffer_window_seconds
        self.min_check_interval_seconds = min_check_interval_seconds

        self._buffer = []
        self._last_check_time = 0.0 # when was gem last told to anaylse transcript


#-----Function recieves a newly transcribed sentence
    def add_transcript(self, text):
        if not text:
            return
 
        now = time.time()
        self._buffer.append((now, text)) # store tuple
        self._trim_buffer(now) # get rid of anything too old. Dont wanna use too much ram/ clog
 
    def _trim_buffer(self, now):
        cutoff = now - self.buffer_window_seconds
        self._buffer = [(ts, text) for ts, text in self._buffer if ts >= cutoff]
 
    def ready_to_check(self):
        now = time.time()
        return (now - self._last_check_time) >= self.min_check_interval_seconds and bool(self._buffer)

 #Main AI Stuff/ Coooool Stuff 
    def check_for_cue(self) -> Optional[MusicCue]:
        if not self._buffer:
            return None
 
        self._last_check_time = time.time()
        combined_text = " ".join(text for _, text in self._buffer)
 
        try:
            response = self.client.generate_content(combined_text)
 
            raw = response.text.strip()
            data = json.loads(raw)
 
            mood = data.get("mood")
            if mood not in VALID_MOODS:
                mood = None
 
            return MusicCue(
                cue_detected=bool(data.get("cue_detected", False)),
                mood=mood,
                confidence=float(data.get("confidence", 0.0)),
                raw_reasoning=data.get("reasoning"),
            )
 
        except json.JSONDecodeError as error:
            raise IntentDetectionError(f"Model did not return valid JSON: {error}") from error
 
        except Exception as error:
            raise IntentDetectionError(f"Intent detection failed: {error}") from error
 
    def clear_buffer(self):
        self._buffer = []
