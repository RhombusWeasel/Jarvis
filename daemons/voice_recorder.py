import pyaudio
import numpy as np
import wave
import webrtcvad
import collections
import time, sys, os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
from utils import logger
log = logger.Logger('recorder', log_level=logger.Logger.DEBUG)

audio_folder = "audio_files"
THRESHOLD = 15000
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = int(RATE * 0.02)
RECORD_SECONDS = 20
WAVE_OUTPUT_FILENAME = "output.wav"
counter = 0


def detect_noise(data, threshold):
    audio_data = np.frombuffer(data, dtype=np.int16)
    peak_value = np.max(np.abs(audio_data))
    if peak_value > threshold:
        log.debug(f'Peak value: {peak_value}')
        return True
    return False


def record_audio():
    global counter
    audio = pyaudio.PyAudio()
    vad = webrtcvad.Vad(2)
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    data = stream.read(CHUNK)
    if detect_noise(data, THRESHOLD):
        log.info('Recording...')
        counter += 1
        frames = collections.deque(maxlen=int(RATE / CHUNK * RECORD_SECONDS))
        frames.append(data)

        non_speech_counter = 0
        non_speech_limit = 20  # Adjust this value to fine-tune the pause duration

        while True:
            data = stream.read(CHUNK)
            if vad.is_speech(data, RATE):
                non_speech_counter = 0
                frames.append(data)
            else:
                non_speech_counter += 1
                if non_speech_counter >= non_speech_limit:
                    break
                log.debug(f'Pause Timer: {non_speech_limit - non_speech_counter}\r')

        wf = wave.open(os.path.join(audio_folder, f'audio_{counter}.wav'), "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
        wf.close()
        log.info(f'audio_{counter}.wav written.')

    return WAVE_OUTPUT_FILENAME

def main():
    while True:
        record_audio()


if __name__ == "__main__":
    log.info('Voice recorder started.')
    main()