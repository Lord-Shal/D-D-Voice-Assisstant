import json
 
from dotenv import load_dotenv
load_dotenv()                                    # read GEMINI_API_KEY from .env
 
import os
import google.generativeai as genai
 
from src.speech.intent_detector import CANDIDATE_MOODS   # the menu of moods to choose from
 
TAGS_FILE = "mood_tags.json"
MODEL = "gemini-3.1-flash-lite"                  # same model your intent detector uses
BATCH_SIZE = 25                                  # tracks per Gemini request
MAX_MOODS_PER_TRACK = 3                          # keeps tags focused
 
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel(
    model_name=MODEL,
    generation_config={"response_mime_type": "application/json"},  # force JSON output
)
 
 
def tag_batch(batch):
    """Ask Gemini for moods for a list of (index, name) pairs. Returns {index: [moods]}."""
    tracks = [{"i": i, "name": name} for i, name in batch]
    prompt = (
        "You are tagging songs for background music in a Dungeons & Dragons session.\n"
        f"Allowed moods: {', '.join(CANDIDATE_MOODS)}\n"
        f"For each track pick 1 to {MAX_MOODS_PER_TRACK} moods from the allowed list that "
        "best describe how it would feel as D&D background music. "
        "Use only the allowed moods.\n"
        'Respond ONLY with JSON in this shape: {"results": [{"i": 0, "moods": ["combat"]}]}\n\n'
        f"Tracks:\n{json.dumps(tracks, ensure_ascii=False)}"
    )
    response = model.generate_content(prompt)
    data = json.loads(response.text)
 
    results = {}
    for item in data.get("results", []):
        moods = [m.lower() for m in item.get("moods", []) if m.lower() in CANDIDATE_MOODS]
        results[item["i"]] = moods[:MAX_MOODS_PER_TRACK]   # drop anything not on the menu
    return results
 
 
def main():
    with open(TAGS_FILE, encoding="utf-8") as f:
        tagged = json.load(f)
 
    todo = [(i, t["name"]) for i, t in enumerate(tagged) if not t.get("moods")]
    print(f"{len(todo)} of {len(tagged)} tracks need moods.")
 
    for start in range(0, len(todo), BATCH_SIZE):
        batch = todo[start:start + BATCH_SIZE]
        try:
            results = tag_batch(batch)
        except Exception as error:               # one bad batch shouldn't stop the rest
            print(f"  batch starting at {start} failed: {error}")
            continue
 
        for i, moods in results.items():
            tagged[i]["moods"] = moods
 
        with open(TAGS_FILE, "w", encoding="utf-8") as f:   # save after every batch
            json.dump(tagged, f, indent=2, ensure_ascii=False)
        print(f"  tagged {min(start + BATCH_SIZE, len(todo))}/{len(todo)}")
 
    print("Done. Open mood_tags.json and fix anything that looks wrong.")
 
 
if __name__ == "__main__":
    main()