"""Fresh runtime health requires usable storage and never resets existing records."""
import importlib
import sqlite3
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def application(monkeypatch, tmp_path):
    monkeypatch.setenv('JWKS', 'http://keycloak.invalid/keys')
    module=importlib.import_module('apps.python.app')
    file=tmp_path/'equipment.db'
    monkeypatch.setattr(module.business,'DB',str(file))
    return module.app,file


def test_fresh_startup_creates_empty_schema_before_health(application):
    app,file=application
    assert not file.exists()
    with TestClient(app) as client:
        assert client.get('/health').status_code==200
        with sqlite3.connect(file) as connection:
            for name in ['assessments','quotes','requests']:
                assert connection.execute('SELECT COUNT(*) FROM '+name).fetchone()==(0,)


def test_existing_records_survive_startup(application):
    app,file=application
    with TestClient(app):
        pass
    with sqlite3.connect(file) as connection:
        connection.execute('INSERT INTO quotes VALUES(?,?)',('preserved','{"amount":78000}'))
    with TestClient(app) as client:
        assert client.get('/health').status_code==200
        with sqlite3.connect(file) as connection:
            assert connection.execute('SELECT * FROM quotes').fetchall()==[('preserved','{"amount":78000}')]


def test_unavailable_storage_prevents_startup(application, monkeypatch):
    app,file=application
    module=importlib.import_module('apps.python.app')
    monkeypatch.setattr(module.business,'DB',str(file.parent/'missing'/'equipment.db'))
    with pytest.raises(sqlite3.OperationalError):
        with TestClient(app):
            pytest.fail('Unusable storage must not report a ready application')
