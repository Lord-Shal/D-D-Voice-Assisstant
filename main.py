import threading

from src.speech.recorder import listen_continuously, RecordingError
from src.speech.transcriber import SpeechTranscriber, TranscriptionError
from src.speech.intent_detector import MusicIntentDetector , IntentDetectionError

MIN_CONFIDENCE = 0.6

def run_listener(transcriber,detector,stop_event):
    last_mood = None
    try:
        for audio in listen_continuously(stop_event):
            if stop_event.is_set():
                break
            try:
                text = transcriber.transcribe(audio)
                if text:
                    print(f"\nTranscript: {text}")
                    detector.add_transcript(text)
            except TranscriptionError as error:
                print(f"\nTranscription error: {error}")

            if detector.ready_to_check():
                try:
                    cue = detector.check_for_cue()
                except IntentDetectionError as error:
                    print(f"\nIntent detection error: {error}")
                    continue
                if cue:
                    print(f"\n[Gemini] detected={cue.cue_detected} mood={cue.mood} "
                          f"conf={cue.confidence:.2f} reason={cue.raw_reasoning}")
                if (cue and cue.cue_detected and cue.mood
                    and cue.confidence >= MIN_CONFIDENCE
                    and cue.mood != last_mood):
                    print(f"Music cue: {cue.mood} ({cue.confidence:.2f} - {cue.raw_reasoning})")
                    last_mood = cue.mood
                    detector.clear_buffer()

    except RecordingError as error:
        print(f"\nRecording error: {error}")
        stop_event.set()

    except Exception as error:
        print(f"\nUnexpected listener error: {error}")
        stop_event.set()

def start_listening(transcriber,detector):
    stop_event = threading.Event()
    listener_thread = threading.Thread(target=run_listener, args=(transcriber,detector,stop_event), daemon=True)
    listener_thread.start()
    return stop_event, listener_thread

def stop_listening(stop_event, listener_thread):
    stop_event.set()

    if listener_thread.is_alive():
        listener_thread.join()

    print("\nListening stopped.")

def main():
    try:
        transcriber = SpeechTranscriber()
        detector = MusicIntentDetector()
    except (TranscriptionError,IntentDetectionError) as error:
        print(f"Startup error: {error}")
        return

    while True:
        print("\n--- D&D Voice Assistant ---")
        print("[S] Start listening")
        print("[Q] Quit")

        choice = input("> ").strip().lower()

        if choice == "q":
            print("Goodbye.")
            break

        if choice != "s":
            print("Invalid option.")
            continue

        stop_event, listener_thread = start_listening(transcriber,detector)

        print("Press Enter to stop listening.")

        try:
            input()
        except KeyboardInterrupt:
            print()

        stop_listening(stop_event, listener_thread)

if __name__ == "__main__":
    main()