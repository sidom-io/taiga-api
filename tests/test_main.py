"""Tests para el módulo principal de FastAPI."""

import pytest
from fastapi.testclient import TestClient


def test_app_startup(client: TestClient):
    """Test que la aplicación inicia correctamente."""
    # Este test verifica que la app se puede instanciar
    assert client.app is not None


def test_debug_endpoints_exist(client: TestClient):
    """Test que los endpoints de debug existen."""
    # Verificar que los endpoints de debug están disponibles
    # Nota: Pueden fallar por falta de configuración, pero deben existir

    response = client.get("/debug/state")
    # El endpoint debe existir (no 404)
    assert response.status_code != 404

    response = client.post("/debug/auth")
    # El endpoint debe existir (no 404)
    assert response.status_code != 404


@pytest.mark.integration
def test_health_check():
    """Test de integración básico."""
    # Este test se marca como integración para ejecutarse por separado
    assert True  # Placeholder para tests de integración reales
