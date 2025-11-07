"""Tests para el cliente de Taiga."""

import pytest
from unittest.mock import AsyncMock, patch

from app.taiga_client import TaigaClient, TaigaClientError


def test_taiga_client_init_with_token():
    """Test inicialización del cliente con token."""
    client = TaigaClient(
        base_url="https://test.example.com/api/v1/",
        auth_token="test_token"
    )
    assert client.base_url == "https://test.example.com/api/v1/"
    assert client.auth_token == "test_token"


def test_taiga_client_init_with_credentials():
    """Test inicialización del cliente con credenciales."""
    client = TaigaClient(
        base_url="https://test.example.com/api/v1/",
        username="test_user",
        password="test_pass"
    )
    assert client.username == "test_user"
    assert client.password == "test_pass"


def test_taiga_client_init_no_auth():
    """Test que falla la inicialización sin autenticación."""
    with pytest.raises(ValueError, match="Se requiere auth_token o username/password"):
        TaigaClient(base_url="https://test.example.com/api/v1/")


def test_base_url_normalization():
    """Test que la URL base se normaliza correctamente."""
    client = TaigaClient(
        base_url="https://test.example.com/api/v1",  # Sin barra final
        auth_token="test_token"
    )
    assert client.base_url == "https://test.example.com/api/v1/"


@pytest.mark.asyncio
async def test_client_lifecycle():
    """Test del ciclo de vida del cliente."""
    client = TaigaClient(
        base_url="https://test.example.com/api/v1/",
        auth_token="test_token"
    )
    
    # Test start
    await client.start()
    assert client._client is not None
    
    # Test close
    await client.close()
    assert client._client is None