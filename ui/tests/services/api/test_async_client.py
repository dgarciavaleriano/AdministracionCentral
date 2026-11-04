import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.api.async_client import AsyncApiClient

@pytest.mark.asyncio
async def test_api_client_stream_chat_success():
    """Valida que AsyncApiClient procesa correctamente el flujo SSE y emite los tokens de texto."""
    mock_lines = [
        'data: {"text": "Hola"}',
        'data: {"text": " mundo"}',
        'data: [DONE]'
    ]

    async def mock_aiter_lines():
        for line in mock_lines:
            yield line

    # Mock de la respuesta HTTP
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.aiter_lines = mock_aiter_lines

    # Mock del contexto asíncrono para client.stream(...)
    mock_stream_context = MagicMock()
    mock_stream_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_stream_context.__aexit__ = AsyncMock(return_value=None)

    # Mock del cliente HTTP de httpx
    mock_client = MagicMock()
    mock_client.stream.return_value = mock_stream_context

    # Mock del contexto asíncrono para httpx.AsyncClient(...)
    mock_client_context = MagicMock()
    mock_client_context.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client_context.__aexit__ = AsyncMock(return_value=None)

    # Interceptamos httpx.AsyncClient apuntando al nuevo archivo
    with patch("services.api.async_client.httpx.AsyncClient", return_value=mock_client_context):
        client = AsyncApiClient(base_url="http://localhost:8080")
        messages = [{"role": "user", "content": "Hola"}]

        # Consumimos el generador asíncrono
        tokens = [token async for token in client.stream_chat(messages)]

        # Validaciones
        assert tokens == ["Hola", " mundo"]
        mock_response.raise_for_status.assert_called_once()