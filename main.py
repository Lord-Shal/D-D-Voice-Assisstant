import threading

from src.speech.recorder import listen_continuously, RecordingError
from src.speech.transcriber import SpeechTranscriber, TranscriptionError

def run_listener(transcriber, stop_event):
    try:
        for audio in listen_continuously(stop_event):
            if stop_event.is_set():
                break

            try:
                text = transcriber.transcribe(audio)
                if text:
                    print(f"\nTranscript: {text}")
            except TranscriptionError as error:
                print(f"\nTranscription error: {error}")

    except RecordingError as error:
        print(f"\nRecording error: {error}")
        stop_event.set()

    except Exception as error:
        print(f"\nUnexpected listener error: {error}")
        stop_event.set()

def start_listening(transcriber):
    stop_event = threading.Event()
    listener_thread = threading.Thread(target=run_listener, args=(transcriber, stop_event), daemon=True)
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
    except TranscriptionError as error:
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

        stop_event, listener_thread = start_listening(transcriber)

        print("Press Enter to stop listening.")

        try:
            input()
        except KeyboardInterrupt:
            print()

        stop_listening(stop_event, listener_thread)

if __name__ == "__main__":
    main()