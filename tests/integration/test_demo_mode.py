"""Integration tests for the read-only demo mode against the real API."""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from provisionR.app import create_app
from provisionR.database import SessionLocal
from provisionR.demo import REFUSAL_DETAIL
from provisionR.models import DBGlobalConfig, DBMachinePasswords

KS_QUERY = "mac=00:11:22:33:44:55&uuid=demo-uuid&serial=DEMO-SN"


@pytest.fixture
def demo_client():
    return TestClient(create_app(demo_mode=True))


def template_dir() -> Path:
    return Path(os.environ["PROVISIONR_TEMPLATE_DIR"])


def machine_count() -> int:
    with SessionLocal() as db:
        return db.query(DBMachinePasswords).count()


def assert_refused(response):
    assert response.status_code == 403
    assert response.json() == {"detail": REFUSAL_DETAIL}


def test_kickstart_generation_is_refused_and_creates_no_machine(demo_client):
    assert_refused(demo_client.get(f"/api/v1/ks?{KS_QUERY}"))
    assert_refused(demo_client.get("/api/v1/ks"))
    assert machine_count() == 0


def test_password_export_is_refused(demo_client):
    assert_refused(demo_client.get("/api/v1/machines/export"))
    assert demo_client.head("/api/v1/machines/export").status_code == 403


def test_config_update_is_refused_and_nothing_changes(demo_client):
    response = demo_client.put(
        "/api/v1/config",
        json={
            "target_os": "Ubuntu25.04",
            "generate_passwords": False,
            "values": {"a": "b"},
        },
    )
    assert_refused(response)
    assert_refused(demo_client.put("/api/v1/config", content=b"not json"))
    with SessionLocal() as db:
        assert db.query(DBGlobalConfig).count() == 0


def test_template_upload_is_refused_and_writes_no_file(demo_client):
    response = demo_client.post(
        "/api/v1/templates",
        files={"file": ("x.ks.j2", b"{{ mac }}", "text/plain")},
        data={"template_name": "demo-upload", "use_as_default": "true"},
    )
    assert_refused(response)
    assert not (template_dir() / "demo-upload.ks.j2").exists()
    assert not (template_dir() / "default.ks.j2").exists()


@pytest.mark.parametrize("method", ["DELETE", "PATCH", "OPTIONS"])
def test_other_methods_are_refused(demo_client, method):
    assert_refused(demo_client.request(method, "/api/v1/config"))


def test_reads_still_work_in_demo_mode(demo_client):
    assert demo_client.get("/api/health").json() == {
        "status": "healthy",
        "service": "provisionR",
    }
    assert demo_client.get("/api/v1/config").status_code == 200
    assert demo_client.get("/api/v1/templates/default").status_code == 200
    assert demo_client.get("/openapi.json").status_code == 200


def test_demo_mode_follows_the_environment(monkeypatch):
    monkeypatch.setenv("PROVISIONR_DEMO_MODE", "true")
    assert_refused(TestClient(create_app()).get(f"/api/v1/ks?{KS_QUERY}"))
    monkeypatch.setenv("PROVISIONR_DEMO_MODE", "false")
    assert TestClient(create_app()).get(f"/api/v1/ks?{KS_QUERY}").status_code == 200


def test_uploaded_templates_render_sandboxed(client: TestClient):
    """An uploaded template cannot reach Python internals through Jinja2."""
    template_dir().mkdir(parents=True, exist_ok=True)
    payload = b"{{ ''.__class__.__mro__[1].__subclasses__() }}"
    upload = client.post(
        "/api/v1/templates",
        files={"file": ("evil.ks.j2", payload, "text/plain")},
        data={"template_name": "sandbox-probe"},
    )
    assert upload.status_code == 200
    try:
        response = client.get(f"/api/v1/ks?{KS_QUERY}&template_name=sandbox-probe")
        assert response.status_code == 500
        assert "is unsafe" in response.json()["detail"]
        assert "<class" not in response.text
    finally:
        (template_dir() / "sandbox-probe.ks.j2").unlink(missing_ok=True)
