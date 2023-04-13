import os, sys
import time
import pyttsx3

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
from utils import logger
log = logger.Logger('orator', log_level=logger.Logger.INFO)

oration_folder = "audio_oration"


engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[3].id)


def speak(text):
    global engine
    engine.say(text)
    engine.runAndWait()


if __name__ == '__main__':
    log.info('Orator started.')
    while True:
        for filename in os.listdir(oration_folder):
            if filename.endswith(".txt"):
                filepath = os.path.join(oration_folder, filename)
                with open(filepath, 'r') as f:
                    txt = f.read()
                f.close()
                os.remove(filepath)
                speak(txt)
        time.sleep(1)