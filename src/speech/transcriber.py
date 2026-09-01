from faster_whisper import WhisperModel
import numpy as np

class SpeechTranscriber:
    def __init__(self):
        self.model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8")

    def transcribe(self, audio):
        if isinstance(audio, np.ndarray):
            audio = audio.astype(np.float32) / 32768.0
            audio = audio.flatten()
        segments, info = self.model.transcribe(
            audio,
            language="en")

        text = " ".join(
            segment.text.strip()
            for segment in segments)

        return text