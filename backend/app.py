from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from sentence_transformers import SentenceTransformer, util
import requests
import base64
import numpy as np
import json


app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


def image_to_base64(file):
    """
    Converts an image file to base64 encoding.

    Args:
    - file: File object representing the image file.

    Returns:
    - str: Base64 encoded string of the image data, or None if error.
    """
    try:
        image_data = file.read()
        base64_representation = base64.b64encode(image_data).decode("utf-8")
        return base64_representation
    except Exception as e:
        print(f"Error: {e}")
        return None


@app.route("/findSimilar", methods=["POST"])
@cross_origin()
def find_similar_images():
    """
    Endpoint to find similar images based on embeddings and search term.

    Expects POST request with form data:
    - embeddings: JSON array of embeddings.
    - ids: JSON array of IDs corresponding to embeddings.
    - searchTerm: Search term to compare against embeddings.

    Uses SentenceTransformer model for embedding similarity calculation.

    Returns:
    - JSON: List of IDs of images similar to the search term.
    """
    embeddings = json.loads(request.form["embeddings"])
    ids = json.loads(request.form["ids"])
    searchTerm = request.form["searchTerm"]
    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
    searchTerm_embedding = model.encode(searchTerm, convert_to_numpy=True)

    # Calculate cosine similarity for each embedding
    results = []
    for idx, embedding in enumerate(embeddings):
        embedding_np = np.array(embedding)
        search_emb = searchTerm_embedding.astype(embedding_np.dtype)
        emb_np_reshaped = embedding_np.reshape(1, -1)
        cosine_sim = util.pytorch_cos_sim(search_emb, emb_np_reshaped).item()

        if cosine_sim > 0.3:
            results.append(ids[idx])

    return jsonify(results)


@app.route("/upload", methods=["POST"])
@cross_origin()
def upload_file():
    """
    Endpoint to handle file uploads and image description retrieval.

    Expects POST request with a file attached and 'name' field.

    Returns:
    - JSON: Response containing AI-generated image description and embedding.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    filename = request.form.get("name", "")
    if filename == "":
        return jsonify({"error": "No selected file"}), 400
    if file:
        base64_image = image_to_base64(file)

        if base64_image:
            payload = {
                "stream": False,
                "image_data": [{"id": 10, "data": base64_image}],
                "prompt": "You are an AI assistant that describes images "
                + "in a descriptive phrase "
                + "between 15 and 30 words. Describe"
                + "everything you see. "
                + "\nUSER: What does the [img-10] contain?\n"
                + "ASSISTANT:",
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                "http://host.docker.internal:8080" + "/completion",
                headers=headers,
                json=payload,
            )
            r = response.json()

            model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
            embedding = model.encode(r["content"], convert_to_numpy=True)

            tensor_json_serial = embedding.tolist()

            return {"answer": r["content"], "embedding": tensor_json_serial}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
