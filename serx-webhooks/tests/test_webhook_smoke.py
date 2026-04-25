"""Smoke tests for serx-webhooks.

Runs without any real Supabase or Doppler config. Environment variables
are set at import time so pydantic-settings doesn't blow up, and
``app.database.get_supabase`` is monkeypatched with an in-memory fake
that mimics the minimal surface area the routers touch (insert,
select+head+count+limit+execute, with unique-violation simulation).
"""

from __future__ import annotations

import json
import os
import uuid
from typing import Any

import pytest

os.environ.setdefault("SERX_SUPABASE_URL", "https://fake.supabase.co")
os.environ.setdefault("SERX_SUPABASE_SERVICE_ROLE_KEY", "fake-service-role-key")
os.environ.setdefault("CAL_WEBHOOK_SECRET", "")
os.environ.setdefault("OPEX_API_BASE_URL", "https://fake.opex.local")
os.environ.setdefault("OPEX_AUTH_TOKEN", "")
os.environ.setdefault("OPEX_DISPATCH_ENABLED", "true")
os.environ.setdefault("OPEX_DISPATCH_TIMEOUT_SECONDS", "10.0")
os.environ.setdefault("OPEX_DISPATCH_MAX_ATTEMPTS", "3")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("APP_NAME", "serx-webhooks")
os.environ.setdefault("APP_VERSION", "0.1.0")
os.environ.setdefault("CORS_ORIGINS", '["*"]')

from fastapi.testclient import TestClient  # noqa: E402

from app import database as db_module  # noqa: E402
from app.main import app  # noqa: E402
from app.routers import cal as cal_router  # noqa: E402
from app.routers import health as health_router  # noqa: E402


class _FakeExecuteResult:
    def __init__(self, data: list[dict[str, Any]]):
        self.data = data


class _FakeQuery:
    def __init__(self, table: _FakeTable, mode: str, row: dict[str, Any] | None = None):
        self._table = table
        self._mode = mode
        self._row = row

    def select(self, *_args, **_kwargs) -> _FakeQuery:
        return _FakeQuery(self._table, "select")

    def limit(self, *_args, **_kwargs) -> _FakeQuery:
        return self

    def execute(self) -> _FakeExecuteResult:
        if self._mode == "insert":
            assert self._row is not None
            key = (self._row.get("source"), self._row.get("event_key"))
            if self._table.should_raise_ready_error:
                raise RuntimeError("readiness boom")
            if key in self._table.seen_keys:
                raise RuntimeError("duplicate key value violates unique constraint (23505)")
            self._table.seen_keys.add(key)
            stored = dict(self._row)
            stored["id"] = str(uuid.uuid4())
            self._table.rows.append(stored)
            return _FakeExecuteResult([stored])
        if self._table.should_raise_ready_error:
            raise RuntimeError("readiness boom")
        return _FakeExecuteResult([])


class _FakeTable:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.seen_keys: set[tuple[str | None, str | None]] = set()
        self.should_raise_ready_error = False

    def insert(self, row: dict[str, Any]) -> _FakeQuery:
        return _FakeQuery(self, "insert", row)

    def select(self, *_args, **_kwargs) -> _FakeQuery:
        return _FakeQuery(self, "select")


class _FakeSupabase:
    def __init__(self) -> None:
        self._tables: dict[str, _FakeTable] = {}

    def table(self, name: str) -> _FakeTable:
        return self._tables.setdefault(name, _FakeTable())


@pytest.fixture
def fake_supabase(monkeypatch: pytest.MonkeyPatch) -> _FakeSupabase:
    fake = _FakeSupabase()
    monkeypatch.setattr(db_module, "get_supabase", lambda: fake)
    monkeypatch.setattr(cal_router, "get_supabase", lambda: fake)
    monkeypatch.setattr(health_router, "get_supabase", lambda: fake)
    return fake


@pytest.fixture
def client(fake_supabase: _FakeSupabase) -> TestClient:
    return TestClient(app)


def _rows_for(fake: _FakeSupabase) -> list[dict[str, Any]]:
    return fake._tables["webhook_events_raw"].rows


def test_liveness(client: TestClient) -> None:
    r = client.get("/health/live")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_readiness_ok(client: TestClient, fake_supabase: _FakeSupabase) -> None:
    fake_supabase.table("webhook_events_raw")  # pre-create
    r = client.get("/health/ready")
    assert r.status_code == 200


def test_readiness_503_on_db_failure(client: TestClient, fake_supabase: _FakeSupabase) -> None:
    fake_supabase.table("webhook_events_raw").should_raise_ready_error = True
    r = client.get("/health/ready")
    assert r.status_code == 503


def test_nested_booking_created(client: TestClient, fake_supabase: _FakeSupabase) -> None:
    body = {
        "triggerEvent": "BOOKING_CREATED",
        "createdAt": "2026-04-21T00:00:00Z",
        "payload": {"uid": "abc", "eventTypeId": 1},
    }
    r = client.post("/webhooks/cal", json=body)
    assert r.status_code == 202
    assert r.json() == {"status": "accepted"}

    rows = _rows_for(fake_supabase)
    assert len(rows) == 1
    row = rows[0]
    assert row["source"] == "cal_com"
    assert row["trigger_event"] == "BOOKING_CREATED"
    assert row["payload"] == body
    assert row["signature_valid"] is None  # no secret set


def test_flat_meeting_started(client: TestClient, fake_supabase: _FakeSupabase) -> None:
    body = {
        "triggerEvent": "MEETING_STARTED",
        "bookingId": 42,
        "roomName": "abc-xyz",
    }
    r = client.post("/webhooks/cal", json=body)
    assert r.status_code == 202

    rows = _rows_for(fake_supabase)
    assert len(rows) == 1
    row = rows[0]
    assert row["trigger_event"] == "MEETING_STARTED"
    assert row["payload"] == body


def test_non_json_body(client: TestClient, fake_supabase: _FakeSupabase) -> None:
    r = client.post(
        "/webhooks/cal",
        content=b"this-is-not-json",
        headers={"content-type": "text/plain"},
    )
    assert r.status_code == 202

    rows = _rows_for(fake_supabase)
    assert len(rows) == 1
    row = rows[0]
    assert row["trigger_event"] is None
    assert row["payload"] == {"_raw_text": "this-is-not-json"}


def test_duplicate_post(client: TestClient, fake_supabase: _FakeSupabase, caplog) -> None:
    body = {"triggerEvent": "BOOKING_CREATED", "payload": {"uid": "dup"}}
    raw = json.dumps(body).encode()

    with caplog.at_level("INFO", logger="serx_webhooks.cal"):
        r1 = client.post(
            "/webhooks/cal",
            content=raw,
            headers={"content-type": "application/json"},
        )
        r2 = client.post(
            "/webhooks/cal",
            content=raw,
            headers={"content-type": "application/json"},
        )
    assert r1.status_code == 202
    assert r2.status_code == 202

    rows = _rows_for(fake_supabase)
    assert len(rows) == 1  # second insert collapsed

    messages = "\n".join(rec.getMessage() for rec in caplog.records)
    assert "webhook_stored" in messages
    assert "webhook_duplicate" in messages
    assert "duplicate=True" in messages
