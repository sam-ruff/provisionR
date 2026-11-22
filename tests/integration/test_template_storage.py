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


def test_upload_larger_than_form_part_limit_is_stored(monkeypatch, tmp_path):
    # FastAPI 0.164+ adds opt-in body and form limits; file parts must stay
    # unlimited by default, beyond Starlette's 1 MiB text-field part size.
    monkeypatch.setenv("PROVISIONR_TEMPLATE_DIR", str(tmp_path / "templates"))
    template = "# {{ mac }}\n" + "%packages\n@core\n%end\n" * 110_000
    assert len(template.encode()) > 2 * 1024 * 1024
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/templates",
            data={"template_name": "large"},
            files={"file": ("large.ks.j2", template, "text/plain")},
        )
        assert response.status_code == 200
        assert client.get("/api/v1/templates/large").text == template


def test_oversized_text_form_field_is_rejected(monkeypatch, tmp_path):
    # Text fields keep Starlette's 1 MiB part limit and are refused before
    # anything is written to the template directory.
    directory = tmp_path / "templates"
    monkeypatch.setenv("PROVISIONR_TEMPLATE_DIR", str(directory))
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/templates",
            data={"template_name": "x" * (1024 * 1024 + 1)},
            files={"file": ("big.ks.j2", "content", "text/plain")},
        )
    assert response.status_code == 400
    assert not any(directory.glob("*.ks.j2"))
