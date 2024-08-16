import pytest
from fastapi.testclient import TestClient
from main import app  # 假设你的 FastAPI 应用程序文件名是 main.py

client = TestClient(app)

def test_generate_image_success():
    response = client.post(
        "/v1/images/generations",
        json={
            "model": "dall-e-3",
            "prompt": "A cute baby sea otter",
            "n": 1,
            "size": "1024x1024"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "created" in data
    assert "data" in data
    assert len(data["data"]) == 1
    assert "url" in data["data"][0]

def test_generate_image_invalid_model():
    response = client.post(
        "/v1/images/generations",
        json={
            "model": "invalid-model",
            "prompt": "A cute baby sea otter",
            "n": 1,
            "size": "1024x1024"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Model not supported"

def test_generate_image_invalid_n_for_dalle3():
    response = client.post(
        "/v1/images/generations",
        json={
            "model": "dall-e-3",
            "prompt": "A cute baby sea otter",
            "n": 2,
            "size": "1024x1024"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "For dall-e-3, only n=1 is supported"

def test_generate_image_invalid_size():
    response = client.post(
        "/v1/images/generations",
        json={
            "model": "dall-e-2",
            "prompt": "A cute baby sea otter",
            "n": 1,
            "size": "invalid-size"
        }
    )
    assert response.status_code == 422  # FastAPI 将返回 422 Unprocessable Entity

def test_generate_image_b64_json_response():
    response = client.post(
        "/v1/images/generations",
        json={
            "model": "dall-e-2",
            "prompt": "A cute baby sea otter",
            "n": 1,
            "response_format": "b64_json",
            "size": "1024x1024"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "created" in data
    assert "data" in data
    assert len(data["data"]) == 1
    assert "b64_json" in data["data"][0]
