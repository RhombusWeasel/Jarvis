import os
import sys
import time
import json
import torch
import whisper

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
from utils import logger
log = logger.Logger('transcriber', log_level=logger.Logger.DEBUG)

audio_folder = "audio_files"
transcriptions_folder = "audio_transcriptions"
device = "cuda" if torch.cuda.is_available() else "cpu"
log.info(f"Set device to {device}")
model = whisper.load_model("large-v2")

def transcribe_audio_files():
    for filename in os.listdir(audio_folder):
        if filename.endswith(".wav"):
            filepath = os.path.join(audio_folder, filename)
            file = filename.split('.')[0]
            result = model.transcribe(filepath, fp16=True)
            os.remove(filepath)
            log.debug(result["text"])
            if len(result['text']) > 10:
                txt = result['text']
                log.debug(txt)
                # Write the transcription to a file
                with open(os.path.join(transcriptions_folder, f'{file}.txt'), 'w') as f:
                    f.write(json.dumps(txt))
                f.close()
                log.info(f"Transcribed {filename} to {file}.txt")

def main():
    while True:
        try:
            transcribe_audio_files()
        except Exception as e:
            log.error(e)
        time.sleep(.1)

if __name__ == "__main__":
    log.info('Transcription service started.')
    main()
