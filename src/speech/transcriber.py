from faster_whisper import WhisperModel

class SpeechTranscriber:
    def __init__(self):
        self.model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8"
        )

    def transcribe(self, audio_path):
        segments, info = self.model.transcribe(
            audio_path,
            language="en"
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
        )

        return text