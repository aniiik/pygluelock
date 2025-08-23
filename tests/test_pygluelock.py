from unittest.mock import patch, AsyncMock
import pytest
import asyncio
from pygluelock.glue_lock import GlueLock
from pygluelock.exceptions import (
    BadRequestException,
)


class DummySession:
    def __init__(self):
        self.get_called = False
        self.post_called = False
        self.last_url = None
        self.last_headers = None
        self.last_json = None
        self.status = 200
        self.response_data = {}
        self.text_data = ""

    def get(self, url, headers=None):
        self.get_called = True
        self.last_url = url
        self.last_headers = headers
        return self

    def post(self, url, headers=None, json=None):
        self.post_called = True
        self.last_url = url
        self.last_headers = headers
        self.last_json = json
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def json(self):
        return self.response_data

    async def text(self):
        return self.text_data

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value


def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_init_sets_attributes():
    lock = GlueLock("user", "pass", api_key="key", lock_id="id", session=DummySession())
    assert lock.username == "user"
    assert lock.password == "pass"
    assert lock.api_key == "key"
    assert lock.lock_id == "id"
    assert isinstance(lock.session, DummySession)


def test_is_connected_property():
    lock = GlueLock("user", "pass", api_key="key", lock_id="id", session=DummySession())
    lock.headers = {"Authorization": "Api-Key key"}
    assert lock.is_connected is True
    lock.api_key = None
    assert lock.is_connected is False


def test_connect_sets_headers():
    session = DummySession()
    lock = GlueLock("user", "pass", api_key="key", lock_id="id", session=session)
    run_async(lock.connect())
    assert lock.headers["Authorization"] == "Api-Key key"


@patch("pygluelock.glue_lock.GlueLock.get_all_locks", new_callable=AsyncMock)
def test_get_lock_id_from_name(mock_get_all_locks):
    mock_get_all_locks.return_value = [
        {"id": "lock1", "name": "Front Door"},
        {"id": "lock2", "name": "Back Door"},
    ]
    session = DummySession()
    lock = GlueLock("user", "pass", api_key="key", lock_id="lock1", session=session)
    lock.headers = {"Authorization": "Api-Key key"}
    result = run_async(lock.get_lock_id_from_name("Front Door"))
    assert result == "lock1"


def test_get_all_locks_success():
    session = DummySession()
    session.response_data = [
        {"id": "lock1", "description": "Front Door"},
        {"id": "lock2", "description": "Back Door"},
    ]
    lock = GlueLock("user", "pass", api_key="key", lock_id="lock1", session=session)
    lock.headers = {"Authorization": "Api-Key key"}
    result = run_async(lock.get_all_locks())
    assert result == [
        {"id": "lock1", "name": "Front Door"},
        {"id": "lock2", "name": "Back Door"},
    ]


def test_get_all_locks_failure():
    session = DummySession()
    session.status = 400
    session.text_data = "Bad Request"
    lock = GlueLock("user", "pass", api_key="key", lock_id="lock1", session=session)
    lock.headers = {"Authorization": "Api-Key key"}
    session.response_data = []
    with pytest.raises(BadRequestException):
        run_async(lock.get_all_locks())


def test_update_calls_methods(monkeypatch):
    lock = GlueLock("user", "pass", api_key="key", lock_id="id", session=DummySession())
    lock.headers = {"Authorization": "Api-Key key"}
    async def dummy_async(): return None
    monkeypatch.setattr(lock, "get_battery_status", dummy_async)
    monkeypatch.setattr(lock, "get_last_event", dummy_async)
    monkeypatch.setattr(lock, "get_serial_number", dummy_async)
    monkeypatch.setattr(lock, "get_description", dummy_async)
    run_async(lock.update())


def test_control_lock_invalid_type():
    lock = GlueLock("user", "pass", api_key="key", lock_id="id", session=DummySession())
    lock.headers = {"Authorization": "Api-Key key"}
    with pytest.raises(ValueError):
        run_async(lock.control_lock("invalid"))
