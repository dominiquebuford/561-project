from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from sentence_transformers import SentenceTransformer, util
import requests
import base64
import numpy as np
import json


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def image_to_base64(file):
    try:
        image_data = file.read()
        base64_representation = base64.b64encode(image_data).decode("utf-8")
        return base64_representation
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/findSimilar', methods = ['POST'])
@cross_origin()
def find_similar_images():
    embeddings = json.loads(request.form['embeddings'])
    ids = json.loads(request.form['ids'])
    searchTerm = request.form['searchTerm']
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    searchTerm_embedding = model.encode(searchTerm, convert_to_numpy=True)

    # Calculate cosine similarity for each embedding
    results = []
    for idx, embedding in enumerate(embeddings):
        embedding_np = np.array(embedding)
        searchTerm_embedding = searchTerm_embedding.astype(embedding_np.dtype)
        cosine_sim = util.pytorch_cos_sim(searchTerm_embedding, embedding_np.reshape(1, -1)).item()
        print(cosine_sim)
        if cosine_sim > 0.3:
            results.append(ids[idx])
    
    return results

@app.route('/upload', methods=['POST'])
@cross_origin()
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    filename = request.form.get('name', '')
    if filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        base64_image = image_to_base64(file)

        if base64_image:
            payload =  {
            "stream":False,
            "image_data":[{"id":10,"data":base64_image}],
            "prompt":"You are a AI assistant that describes images in a single short, descriptive phrase no longer than 10 words. Avoid lots of filler words.\nUSER: What does the [img-10] contain?\nASSISTANT:"
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post('http://localhost:8080/completion', headers=headers, json=payload)
            print(response)
            r = response.json()

            model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
            embedding = model.encode(r["content"], convert_to_numpy=True)

            tensor_json_serializable = embedding.tolist()

            return {'answer':r["content"], 'embedding':tensor_json_serializable}
        


if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000)