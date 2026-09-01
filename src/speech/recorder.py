import queue
import sounddevice as sd
import numpy as np

def audio_level(audio):
    audio = audio.astype(np.float32)
    return np.sqrt(np.mean(audio ** 2))

def listen_continuously(
    stop_event,
    sample_rate=16000,
    block_duration=0.1,
    silence_duration=1.0,
    silence_threshold=300,):
    audio_queue = queue.Queue()
    block_size = int(sample_rate * block_duration)
    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_queue.put(indata.copy())

    print("Listening...")
    speech_chunks = []
    is_speaking = False
    silence_time = 0.0
    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
        blocksize=block_size,
        callback=callback,):
        while not stop_event.is_set():
            try:
                chunk = audio_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            level = audio_level(chunk)
            if level > silence_threshold:
                is_speaking = True
                silence_time = 0.0
                speech_chunks.append(chunk)

            elif is_speaking:
                speech_chunks.append(chunk)
                silence_time += block_duration
                if silence_time >= silence_duration:
                    audio = np.concatenate(
                        speech_chunks,
                        axis=0)
                    
                    yield audio
                    speech_chunks = []
                    is_speaking = False
                    silence_time = 0.0
    print("Stopped listening.")