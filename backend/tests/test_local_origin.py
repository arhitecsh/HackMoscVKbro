"""The local site works whether it is opened as 127.0.0.1 or localhost; other sites stay rejected."""
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, 'database', tmp_path / 'origin.sqlite3')
    monkeypatch.setattr(settings, 'storage', tmp_path / 'data')
    monkeypatch.setattr(settings, 'mode', 'demo')
    monkeypatch.setattr(settings, 'email_verification_required', False)
    monkeypatch.setattr(settings, 'public_url', 'http://127.0.0.1:8000')
    monkeypatch.setattr(settings, 'origins', [])
    with TestClient(app) as client:
        yield client


def register(client, origin, email):
    return client.post('/api/auth/register', headers={'Origin': origin, 'Sec-Fetch-Site': 'same-origin'}, json={
        'email': email, 'password': 'Example-password-387', 'first_name': 'Анна', 'last_name': 'Тестовая'})


@pytest.mark.parametrize('origin', ['http://127.0.0.1:8000', 'http://localhost:8000', 'http://[::1]:8000'])
def test_registration_works_from_any_local_name(client, origin):
    assert register(client, origin, 'local@example.test').status_code == 201


@pytest.mark.parametrize('origin', ['http://localhost:9000', 'https://localhost:8000', 'http://evil.example:8000'])
def test_other_origins_are_still_rejected(client, origin):
    assert register(client, origin, 'other@example.test').status_code == 403
