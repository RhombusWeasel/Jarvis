# flask_web_server_daemon.py

from flask import Flask, send_from_directory
import logging
import os, sys

log = logging.getLogger('werkzeug')
log.level = logging.ERROR
log.disabled = True
log = logging.getLogger('flask_web_server_daemon')
log.level = logging.ERROR
log.disabled = True

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
from utils import logger
log = logger.Logger('web-code', log_level=logger.Logger.INFO)

app = Flask(__name__)

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
log.info(f'Path: {path}')

@app.route('/')
def serve_code_editor():
    return send_from_directory(path, 'code_editor.html')

if __name__ == '__main__':
    try:
        log.info("Code-Edit serving on http://127.0.0.1:8000")
        app.run(host='0.0.0.0', port=8000)
    except KeyboardInterrupt:
        pass
    log.info("Flask web server stopped")
