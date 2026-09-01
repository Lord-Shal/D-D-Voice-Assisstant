import threading
from src.speech.recorder import listen_continuously
from src.speech.transcriber import SpeechTranscriber

def run_listener(transcriber, stop_event):
    for audio in listen_continuously(stop_event):
        print("\nSpeech detected. Transcribing...")
        text = transcriber.transcribe(audio)
        if text:
            print(f"Transcript: {text}")

def main():
    transcriber = SpeechTranscriber()
    while True:
        input("\nPress Enter to start listening...")
        stop_event = threading.Event()
        listener_thread = threading.Thread(
            target=run_listener,
            args=(transcriber, stop_event)
        )

        listener_thread.start()
        input("Press Enter to stop listening...\n")
        stop_event.set()
        listener_thread.join()
        print("\nListening stopped.")
        choice = input("Press Enter to listen again, or type q to quit: ")
        if choice.lower() == "q":
            break

if __name__ == "__main__":
    main()