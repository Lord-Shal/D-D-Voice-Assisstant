from src.speech.recorder import record_audio
from src.speech.transcriber import SpeechTranscriber

def main():
    transcriber = SpeechTranscriber()
    input("Press Enter to start recording...")
    audio_path = record_audio(
        duration=5
    )

    text = transcriber.transcribe(audio_path)
    print("\nTranscript:")
    print(text)

if __name__ == "__main__":
    main()