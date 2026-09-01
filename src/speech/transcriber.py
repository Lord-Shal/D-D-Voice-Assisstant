from faster_whisper import WhisperModel
import numpy as np

class TranscriptionError(Exception):
    pass

class SpeechTranscriber:
    def __init__(self):
        try:
            self.model = WhisperModel("small", device="cpu", compute_type="int8")
        except Exception as error:
            raise TranscriptionError(f"Could not load Whisper model: {error}") from error

    def transcribe(self, audio):
        try:
            if audio is None:
                return ""

            if isinstance(audio, np.ndarray):
                if audio.size == 0:
                    return ""

                audio = audio.astype(np.float32) / 32768.0
                audio = audio.flatten()

            segments, info = self.model.transcribe(audio, language="en")
            text = " ".join(segment.text.strip() for segment in segments if segment.text.strip())
            return text

        except Exception as error:
            raise TranscriptionError(f"Transcription failed: {error}") from error