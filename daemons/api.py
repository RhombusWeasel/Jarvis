from flask import Flask, request, jsonify
import openai, json, time, sys, os
import logging

log = logging.getLogger('werkzeug')
log.level = logging.ERROR
log.disabled = True
log = logging.getLogger('flask_web_server_daemon')
log.level = logging.ERROR
log.disabled = True

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
from utils import logger
log = logger.Logger('api', log_level=logger.Logger.INFO)

app = Flask(__name__)

def timestamp():
	return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

with open('secrets.json') as f:
    secrets = json.load(f)
    f.close()

openai.api_key = secrets['api_key']

prompt = """
You are now controlling the API for the Jarvis AI.  You can use this to control the AI and get information from it.
Below are the keys you have available to send in your responses.  You can send multiple keys at once, but only one of each type.
Not all keys are required for each query, only include the keys that are required for the query.
KEYS:
{
    "Jarvis": "A text response...", //These messages are read aloud to the user. Always include a verbal response
    "WEB": "A link...", // Automatically loaded in the users browser. No nsfw content allowed.
    "MEMORY": "A memory...", // If there is something that you feel is important information to the user, send it here.
    "GOOGLE": "A search query...",  // These searches will be opened in a browser and displayed to the user.  Use for current events like movie listings or train timetables.
    "FILE": {"filename": "example_file.ext", "filedata": "print('example')"}, // If you are asked to write something to disk the respond with this key.  All filenames should be lowercase with underscores between words.
    "READ_WEBPAGE": Boolean, // If you are asked to read a webpage, respond with this key.
    "READ_FILE": "path/to/example_file.ext", // If you are asked to read a file, respond with this key filled with the given filepath.
    "CODE_EXAMPLE": {"language": "python", "code": "print('Hello World!')"}, // If you are asked to provide any code, respond with the code in this format.
    "SAVE_PAGE": "example_file.ext", // If you are asked to save a page, respond with this key and pass back the filename given.
}

RULES:
1. Fill out correct values for the required keys based on the context of the query and leave out any keys not required.
2. The 'Jarvis' key is always required, Verbal responses to the user should be in the persona of Jarvis from the Iron Man movies.
3. If you require more information from the user to complete the task use the 'Jarvis' key to convey your question.
4. It is possible the user is wanting a text response from your persona, factor this into your reasoning
5. Any information marked MEMORY: is always reliable information.
6. Any information marked DATA: has been sent by the user.
7. Reading webpages incurs a cost to the user, use only if asked.
8. Only communicate to the user using the Jarvis key, no code is to be put in this response.
9. All code must be sent in the CODE_EXAMPLE key do not use triple backticks.  Do not include code examples unless explicitly asked for code.
10. Memories you wish to store should be sentences most likely to be returned from a vector database search when the topic is queried by the user
11. Memories you have seen in the past should not be stored, only memories you have created.

The current date and time is """+timestamp()+"""

All responses MUST be an RFC8259 compliant JSON object follow this format without deviation.
Any deviation will result in an error and the query will be aborted.
What is the correct JSON response for the users query below?  No explanations are required, just the JSON response.
"""
msg = []


def add_message(queue, role, content):
    queue.append({
        "role": role,
        "content": content
    })


def print_tokens(response):
    usage = response.usage
    log.data('===========TOKENS===========')
    if usage['total_tokens'] <=2000:
        log.data(f'Used {usage["total_tokens"]} tokens.')
    elif usage['total_tokens'] <= 3000:
        log.warn(f'Used {usage["total_tokens"]} tokens.')
    elif usage['total_tokens'] <= 3500:
        log.error(f'Used {usage["total_tokens"]} tokens.')
        log.info('Clearing chat history')
        clear()


def get_35_response(msg):
    log.info(f'User: {msg[-1]["content"]}')
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=msg
    )
    print_tokens(response)
    txt = response.choices[0].message.content.strip()
    log.data(f'Jarvis: {txt}')
    return txt


@app.route('/ask35', methods=['POST'])
def process_transcription():
    m = []
    transcription = request.json['text']
    prefs = request.json['prefs']
    if not transcription or transcription == '':
        return jsonify({"error": "No transcription provided."}), 400
    
    add_message(m, 'system', json.dumps(prefs, indent=2))
    add_message(m, 'system', prompt)
    add_message(m, 'user', transcription)
    response = get_35_response(m)
    return {"response": response}, 200


@app.route('/get_history', methods=['GET'])
def get_history():
    global msg
    return jsonify(msg), 200


@app.route('/clear_history', methods=['POST'])
def clear():
    global msg
    msg = []
    add_message(msg, 'system', prompt)
    return {"response": "Cleared"}, 200

if __name__ == "__main__":
    log.info('API started.')
    add_message(msg, 'system', prompt)
    app.run(host='0.0.0.0', port=5000)