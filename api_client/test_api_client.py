# test_api_client.py
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
import requests

from api_client import APIClient
from config import NON_PROD_CONFIG
from token_manager import TokenManager


@pytest.fixture
def api_client():
    return APIClient(NON_PROD_CONFIG)


@pytest.fixture
def token_manager():
    return TokenManager()


@patch("token_manager.requests.post")
def test_get_token(mock_post, token_manager):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "test_token"}

    token_manager.fetch_token(NON_PROD_CONFIG)
    assert token_manager.token == "test_token"
    assert token_manager.token_expires_at is not None
    assert token_manager.token_expires_at > datetime.now()


@patch("token_manager.requests.post")
def test_fetch_token_http_error(mock_post, token_manager):
    mock_post.return_value.status_code = 401
    mock_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError

    with pytest.raises(Exception) as exc_info:
        token_manager.fetch_token(NON_PROD_CONFIG)
    assert "HTTP error occurred" in str(exc_info.value)


@patch("api_client.requests.get")
@patch.object(TokenManager, "get_token")
def test_get_with_valid_token(mock_get_token, mock_get, api_client):
    token_manager = TokenManager()
    token_manager.token = "valid_token"
    token_manager.token_expires_at = datetime.now() + timedelta(hours=1)
    mock_get_token.return_value = "valid_token"
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"key": "value"}

    response = api_client.get("test-endpoint")
    assert response == {"key": "value"}
    mock_get_token.assert_called_once()


@patch("api_client.requests.get")
@patch.object(TokenManager, "get_token")
def test_get_with_expired_token(mock_get_token, mock_get, api_client):
    token_manager = TokenManager()
    token_manager.token = "expired_token"
    token_manager.token_expires_at = datetime.now() - timedelta(hours=1)
    mock_get_token.return_value = "expired_token"
    mock_get.return_value.status_code = 401
    mock_get.side_effect = [
        requests.exceptions.HTTPError(
            response=type("obj", (object,), {"status_code": 401})
        ),
        pytest.mock.Mock(status_code=200, json=lambda: {"key": "value"}),
    ]

    with patch("token_manager.requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "new_token"}

        with pytest.raises(Exception) as exc_info:
            api_client.get("test-endpoint")
        assert "Token expired and re-fetched" in str(exc_info.value)


@patch("api_client.requests.post")
@patch.object(TokenManager, "get_token")
def test_post(mock_get_token, mock_post, api_client):
    token_manager = TokenManager()
    token_manager.token = "valid_token"
    token_manager.token_expires_at = datetime.now() + timedelta(hours=1)
    mock_get_token.return_value = "valid_token"
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"key": "value"}

    response = api_client.post("test-endpoint", data={"data": "value"})
    assert response == {"key": "value"}
    mock_get_token.assert_called_once()


@patch("api_client.requests.put")
@patch.object(TokenManager, "get_token")
def test_put(mock_get_token, mock_put, api_client):
    token_manager = TokenManager()
    token_manager.token = "valid_token"
    token_manager.token_expires_at = datetime.now() + timedelta(hours=1)
    mock_get_token.return_value = "valid_token"
    mock_put.return_value.status_code = 200
    mock_put.return_value.json.return_value = {"key": "value"}

    response = api_client.put("test-endpoint", data={"data": "value"})
    assert response == {"key": "value"}
    mock_get_token.assert_called_once()


@patch("api_client.requests.delete")
@patch.object(TokenManager, "get_token")
def test_delete(mock_get_token, mock_delete, api_client):
    token_manager = TokenManager()
    token_manager.token = "valid_token"
    token_manager.token_expires_at = datetime.now() + timedelta(hours=1)
    mock_get_token.return_value = "valid_token"
    mock_delete.return_value.status_code = 200
    mock_delete.return_value.json.return_value = {"key": "value"}

    response = api_client.delete("test-endpoint")
    assert response == {"key": "value"}
    mock_get_token.assert_called_once()
