import numpy as np
import hnswlib
import os, sys, json
from sentence_transformers import SentenceTransformer
from flask import Flask, request, jsonify
import logging

log = logging.getLogger('werkzeug')
log.level = logging.ERROR
log.disabled = True
log = logging.getLogger('flask_web_server_daemon')
log.level = logging.ERROR
log.disabled = True

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
from utils import logger
log = logger.Logger('memory', log_level=logger.Logger.INFO)

log.info('Initializing memory module...')
app = Flask(__name__)

# Initialize Sentence Transformer
log.info('Initializing Sentence Transformer...')
model = SentenceTransformer('paraphrase-distilroberta-base-v2')

# Initialize HNSWLIB index
dimension = 768  # Default dimension for the chosen Sentence Transformer model
index = hnswlib.Index(space='cosine', dim=dimension)
index.init_index(max_elements=10000, ef_construction=400, M=200)
index.set_ef(200)

text_data = []

def save_memory(file_name='memory.json'):
    with open(file_name, 'w') as f:
        json.dump(text_data, f)

@app.route('/save_memory', methods=['GET'])
def save_memory_endpoint():
    try:
        save_memory()
        return jsonify({'message': 'Memory saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/add', methods=['POST'])
def add_text():
    text = request.json['text']
    embedding = model.encode([text])[0]
    normalized_embedding = embedding / np.linalg.norm(embedding)
    index.add_items(np.array([normalized_embedding]))
    text_data.append(text)
    log.info(text)
    save_memory()
    return jsonify({'message': 'Text added successfully', 'id': len(text_data) - 1})


@app.route('/search', methods=['POST'])
def search():
    try:
        query = request.json['query']
    except KeyError:
        return jsonify({'error': 'Missing query parameter in JSON'}), 400

    k = min(request.json.get('k', 5), len(text_data))

    query_embedding = model.encode([query])[0]
    normalized_query_embedding = query_embedding / np.linalg.norm(query_embedding)

    try:
        labels, distances = index.knn_query(np.array([normalized_query_embedding]), k=k)
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500

    neighbors = labels.tolist()
    distances = distances.tolist()

    # Retrieve the text for each neighbor
    neighbor_texts = [text_data[index] for index, distance in zip(neighbors[0], distances[0])]

    return jsonify({
        'neighbors': neighbors,
        'distances': distances,
        'texts': neighbor_texts
    })


@app.route('/view_memory', methods=['GET'])
def view_memory():
    return jsonify({'memory': text_data})


def load_memory(file_name='memory.json'):
    log.data(f'Loading memory from {file_name}')
    global text_data

    if not os.path.exists(file_name):
        log.data(f'File {file_name} does not exist')
        return

    with open(file_name, 'r') as f:
        text_data = json.load(f)

    # Add the text_data to the HNSWLIB index
    embeddings = model.encode(text_data)
    normalized_embeddings = embeddings / np.linalg.norm(embeddings, axis=1)[:, None]
    index.add_items(normalized_embeddings)
    log.data(f'Loaded {len(text_data)} items into memory')

# Call load_memory during initialization

if __name__ == '__main__':
    load_memory()
    log.info('Starting webserver...')
    app.run(debug=True, port=9001)
