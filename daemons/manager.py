import utils.webtools as webtools
import requests
import signal
import json
import time
import sys
import os


dirs = [
	'audio_files',
	'audio_oration',
	'audio_requests',
	'audio_transcriptions',
	'files'
]

for d in dirs:
	if not os.path.exists(d):
		os.mkdir(d)

def handle_termination_signal(signum, frame):
    print("Termination signal received, executing cleanup function...")
    # Your cleanup function here
    sys.exit(0)


# Register the signal handler
signal.signal(signal.SIGTERM, handle_termination_signal)

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
from utils import logger
log = logger.Logger('manager', log_level=logger.Logger.INFO)
import daemons.utils.json_validator as json_validator


pref_file = 'preferences.json'
if os.path.exists(pref_file):
	with open(pref_file, 'r') as f:
			prefs = json.load(f)


def timestamp():
	return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def store_preferences():
    with open(pref_file, 'w') as f:
        json.dump(prefs, f)


transcriptions_folder = "audio_transcriptions"
requests_folder = "audio_requests"
oration_folder = "audio_oration"
api_server = "http://127.0.0.1:5000"
memory_api = "http://127.0.0.1:9001"

def parse_webpage(y):
	txt = webtools.get_text_from_url(webtools.browser.current_url)
	log.data(f'Webpage approx tokens is {len(txt) / 4}')
	return txt


def reset_history(txt):
	data = requests.post(f'{api_server}/clear_history')
	log.info(data)


def save_page_to_file(name):
	with open(f'files/{name}', 'w') as f:
		f.write(parse_webpage())
	f.close()


def store_memory(txt):
	data = requests.post(f'{memory_api}/add', json={'text': txt})
	log.info(data)


commands = {
	"clear history": reset_history,
	"save disk file": save_page_to_file,
}
features = {
	'GOOGLE': webtools.google_it,
	"WEB": webtools.new_tab,
	"MEMORY": store_memory,
	"READ_WEBPAGE": parse_webpage,
	"CODE_EXAMPLE": webtools.open_code_editor,
	"SAVE_PAGE": save_page_to_file,
}


# This function processes transcriptions from a folder and sends them to an API server for processing.
def main():
	# Declare global variables commands and features
	global commands, features, prefs
	
	# Loop through all files in the transcriptions folder
	for filename in os.listdir(transcriptions_folder):
		# Check if file is a text file
		if filename.endswith(".txt"):
			# Get the full path of the file
			filepath = os.path.join(transcriptions_folder, filename)
			
			# Open the file and read its contents
			with open(filepath, 'r') as f:
				txt = f.read()
			f.close()
			
			# Remove the file
			os.remove(filepath)
			
			# Log the data
			log.data(txt)
			# Get a deep copy of the text
			req_str = ''
			# Call the memory API to get the response.
			data = requests.post(f'{memory_api}/search', json={'query': txt}).json()
			log.info(data)
			for memory in data['texts']:
					req_str += f"""MEMORY: {memory}\n"""
			
			# Check if any of the names in the list are mentioned in the text
			triggered = False
			names = ['Jarvis', 'Travis', 'Janice', 'Jervis']
			for name in names:
				if name in txt:
					triggered = True
					break
						
			# If one of the names is mentioned, send the text to the API server for processing
			if triggered:
				data = requests.post(f'{api_server}/ask35', json={'text': req_str + '\n' + txt, 'prefs': prefs})
				response = data.json()['response']
				
				# Log the response
				log.json(response)
				
				# Parse the JSON string into a dictionary
				commands = json_validator.parse_json_string(response)
				
				# Write the Jarvis command to a file
				with open(os.path.join(oration_folder, filename), 'w') as f:
					f.write(commands['Jarvis'])
				f.close()

				# Execute the other commands if they are not None or 'None'
				for key in commands:
					if key in features and commands[key] is not None and commands[key] != 'None':
						features[key](commands[key])



if __name__ == '__main__':
	while True:
		try:
			main()
		except Exception as e:
			log.error(e)
		time.sleep(0.1)
