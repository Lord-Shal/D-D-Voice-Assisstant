import queue
import sounddevice as sd
import numpy as np
import torch

from silero_vad import load_silero_vad, VADIterator

class RecordingError(Exception):
    pass

def listen_continuously(stop_event, sample_rate=16000, silence_duration=1000, speech_threshold=0.5):
    audio_queue = queue.Queue()
    block_size = 512

    try:
        vad_model = load_silero_vad()
        vad_iterator = VADIterator(vad_model, threshold=speech_threshold, sampling_rate=sample_rate, min_silence_duration_ms=silence_duration)
    except Exception as error:
        raise RecordingError(f"Could not load VAD model: {error}") from error

    def callback(indata, frames, time, status):
        if status:
            print(f"Audio warning: {status}")

        audio_queue.put(indata.copy())

    speech_chunks = []
    is_speaking = False

    try:
        with sd.InputStream(samplerate=sample_rate, channels=1, dtype="int16", blocksize=block_size, callback=callback):
            print("Listening...")

            while not stop_event.is_set():
                try:
                    chunk = audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                audio = chunk.flatten().astype(np.float32) / 32768.0
                audio_tensor = torch.from_numpy(audio)

                speech_event = vad_iterator(audio_tensor)

                if speech_event and "start" in speech_event:
                    is_speaking = True
                    speech_chunks = [chunk]

                elif is_speaking:
                    speech_chunks.append(chunk)

                if speech_event and "end" in speech_event and is_speaking:
                    audio = np.concatenate(speech_chunks, axis=0)
                    yield audio

                    speech_chunks = []
                    is_speaking = False

            if is_speaking and speech_chunks:
                audio = np.concatenate(speech_chunks, axis=0)
                yield audio

    except sd.PortAudioError as error:
        raise RecordingError(f"Could not access microphone: {error}") from error

    except Exception as error:
        raise RecordingError(f"Unexpected recording error: {error}") from error

    finally:
        vad_iterator.reset_states()
        print("Recorder stopped.")