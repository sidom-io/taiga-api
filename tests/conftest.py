"""Configuración compartida para tests de pytest."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Cliente de prueba para FastAPI."""
    return TestClient(app)


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Variables de entorno mock para tests."""
    monkeypatch.setenv("TAIGA_BASE_URL", "https://test-taiga.example.com/api/v1/")
    monkeypatch.setenv("TAIGA_AUTH_TOKEN", "test_token_123")
    monkeypatch.setenv("TAIGA_TOKEN_TTL", "3600")