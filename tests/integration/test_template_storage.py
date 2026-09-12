from fastapi.testclient import TestClient

from provisionR.app import create_app
from provisionR.template_storage import BUNDLED_TEMPLATES


def test_upload_survives_application_restart_and_is_used_for_generation(
    monkeypatch, tmp_path
):
    directory = tmp_path / "persistent" / "templates"
    monkeypatch.setenv("PROVISIONR_TEMPLATE_DIR", str(directory))
    bundled_default = (BUNDLED_TEMPLATES / "default.ks.j2").read_bytes()
    template = "persistent {{ mac }} {{ serial }}"
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/templates",
            data={"template_name": "migration", "use_as_default": "true"},
            files={"file": ("migration.ks.j2", template, "text/plain")},
        )
        assert response.status_code == 200
    with TestClient(create_app()) as client:
        assert client.get("/api/v1/templates/migration").text == template
        assert client.get("/api/v1/templates/default").text == template
        response = client.get(
            "/api/v1/ks",
            params={
                "mac": "00:11:22:33:44:55",
                "uuid": "migration-test",
                "serial": "fixture",
            },
        )
        assert response.status_code == 200
        assert response.text == "persistent 00:11:22:33:44:55 fixture"
    assert (BUNDLED_TEMPLATES / "default.ks.j2").read_bytes() == bundled_default


def test_empty_persistent_directory_reads_bundled_default(monkeypatch, tmp_path):
    monkeypatch.setenv("PROVISIONR_TEMPLATE_DIR", str(tmp_path / "not-created"))
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/templates/default")
        assert response.status_code == 200
        assert response.text == (BUNDLED_TEMPLATES / "default.ks.j2").read_text()
