from pathlib import Path
from types import SimpleNamespace

import numpy as np
from fastapi.testclient import TestClient

from src.food11 import serve


class FakeModel:
    def predict(self, batch):
        assert batch.shape == (1, 3, 128, 128)
        assert np.isfinite(batch).all()
        # The real model returns logits, not probabilities.
        return np.log([[0.90] + [0.01] * 10])


def test_health_and_missing_model(monkeypatch):
    monkeypatch.setenv("SKIP_MODEL", "1")
    with TestClient(serve.app) as client:
        assert client.get("/health").status_code == 200
        assert client.post("/predict", files={"file": ("x.jpg", b"x")}).status_code == 503


def test_predict(monkeypatch):
    monkeypatch.setenv("SKIP_MODEL", "1")
    with TestClient(serve.app) as client:
        monkeypatch.setattr(serve, "model", FakeModel())
        image = Path(__file__).parent / "fixtures/bread.jpg"
        response = client.post("/predict", files={"file": ("bread.jpg", image.read_bytes(), "image/jpeg")})
        assert response.status_code == 200
        assert response.json()["category"] == "Bread"
        assert abs(response.json()["confidence"] - 0.90) < 1e-6
        assert client.post("/predict", files={"file": ("bad.jpg", b"bad")}).status_code == 400


def test_startup_loads_configured_model(monkeypatch):
    monkeypatch.delenv("SKIP_MODEL", raising=False)
    monkeypatch.setenv("MODEL_URI", "models:/food11/Staging")
    calls = []
    monkeypatch.setattr(serve, "mlflow", SimpleNamespace(pyfunc=SimpleNamespace(
        load_model=lambda uri, **kw: calls.append(uri) or FakeModel())))
    with TestClient(serve.app):
        assert calls == ["models:/food11/Staging"]
        assert serve.model is not None
