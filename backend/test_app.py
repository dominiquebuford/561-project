# test_app.py

import pytest
import json
from unittest.mock import patch, Mock
import numpy as np
from app import app, image_to_base64


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_image_to_base64_success():
    with open("tests/test_image.jpg", "rb") as file:
        base64_string = image_to_base64(file)
        assert base64_string is not None


def test_find_similar_images(client):
    mock_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
    mock_ids = ["id1", "id2", "id3"]
    mock_search_term = "example search term"

    with patch('app.SentenceTransformer') as mock_model:
        mock_instance = mock_model.return_value
        mock_instance.encode.return_value = np.array([0.1, 0.2, 0.3])

        response = client.post('/findSimilar', data={
            'embeddings': json.dumps(mock_embeddings),
            'ids': json.dumps(mock_ids),
            'searchTerm': mock_search_term
        })

        assert response.status_code == 200
        assert json.loads(response.data) == ["id1", "id2", "id3"]


def test_upload_file_no_file(client):
    response = client.post('/upload', data={})
    assert response.status_code == 400
    assert response.get_json() == {'error': 'No file part'}


def test_upload_file_no_filename(client):
    data = {
        'file': (open('tests/test_image.jpg', 'rb'), 'test_image.jpg')
    }
    response = client.post('/upload', data=data)
    assert response.status_code == 400
    assert response.get_json() == {'error': 'No selected file'}


@patch('app.requests.post')
@patch('app.SentenceTransformer')
def test_upload_file_success(mock_model, mock_requests, client):
    mock_model_instance = mock_model.return_value
    mock_model_instance.encode.return_value = np.array([0.1, 0.2, 0.3])

    mock_response = Mock()
    mock_response.json.return_value = {"content": "A descriptive phrase"}
    mock_requests.return_value = mock_response

    data = {
        'file': (open('tests/test_image.jpg', 'rb'), 'test_image.jpg'),
        'name': 'test_image'
    }
    response = client.post('/upload', data=data,
                           content_type='multipart/form-data')

    assert response.status_code == 200
    response_data = response.get_json()
    assert 'answer' in response_data
    assert 'embedding' in response_data
    assert response_data['answer'] == 'A descriptive phrase'
    assert response_data['embedding'] == [0.1, 0.2, 0.3]
