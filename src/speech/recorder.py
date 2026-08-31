import queue
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

def record_audio(
    output_path="recording.wav",
    sample_rate=16000
):
    audio_queue = queue.Queue()
    audio_chunks = []
    def callback(indata, frames, time, status):
        if status:
            print(status)

        audio_queue.put(indata.copy())

    print("Recording...")
    print("Press Enter to stop.")
    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
        callback=callback
    ):
        input()

        while not audio_queue.empty():
            audio_chunks.append(audio_queue.get())

    if not audio_chunks:
        print("No audio was recorded.")
        return None

    audio = np.concatenate(audio_chunks, axis=0)
    write(
        output_path,
        sample_rate,
        audio
    )

    print("Recording complete.")
    return output_path