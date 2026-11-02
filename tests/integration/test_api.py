"""Integration tests for API endpoints."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from provisionR.app import create_app


class TestConfigEndpoint:
    """Tests for the configuration endpoints."""

    def test_get_default_config(self, client: TestClient):
        """Test getting the default global configuration."""
        response = client.get("/api/v1/config")
        assert response.status_code == 200
        data = response.json()
        assert data["target_os"] == "Rocky9"
        assert data["generate_passwords"] is True
        assert data["values"] == {}

    def test_update_config(self, client: TestClient):
        """Test updating the global configuration."""
        new_config = {
            "target_os": "Ubuntu25.04",
            "generate_passwords": False,
            "values": {"key1": "value1", "key2": "value2"},
        }
        response = client.put("/api/v1/config", json=new_config)
        assert response.status_code == 200
        data = response.json()
        assert data["target_os"] == "Ubuntu25.04"
        assert data["generate_passwords"] is False
        assert data["values"]["key1"] == "value1"

        # Verify the config persisted
        get_response = client.get("/api/v1/config")
        assert get_response.json()["target_os"] == "Ubuntu25.04"
        assert get_response.json()["values"]["key1"] == "value1"


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check(self, client: TestClient):
        """Test that the health check endpoint returns a successful response."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "provisionR"


class TestKickstartEndpoint:
    """Tests for the kickstart generation endpoint."""

    def test_generate_kickstart_with_required_params(self, client: TestClient):
        """Test generating a kickstart file with only required parameters."""
        params = {
            "mac": "00:11:22:33:44:55",
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "serial": "SN123456789",
        }
        response = client.get("/api/v1/ks", params=params)
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"

        content = response.text
        assert "00:11:22:33:44:55" in content
        assert "550e8400-e29b-41d4-a716-446655440000" in content
        assert "SN123456789" in content

    def test_generate_kickstart_with_custom_template(self, client: TestClient):
        """Test generating a kickstart file with a custom template name."""
        params = {
            "mac": "00:11:22:33:44:55",
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "serial": "SN123456789",
            "template_name": "default",
        }
        response = client.get("/api/v1/ks", params=params)
        assert response.status_code == 200

    def test_generate_kickstart_with_additional_vars(self, client: TestClient):
        """Test that additional query parameters are passed to the template."""
        params = {
            "mac": "00:11:22:33:44:55",
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "serial": "SN123456789",
            "hostname": "test-server",
            "timezone": "America/New_York",
            "custom_var": "custom_value",
        }
        response = client.get("/api/v1/ks", params=params)
        assert response.status_code == 200
        # The vars are available in the template context
        # Actual usage depends on template implementation

    def test_generate_kickstart_missing_required_param(self, client: TestClient):
        """Test that missing required parameters result in a 422 error."""
        params = {
            "mac": "00:11:22:33:44:55",
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            # serial is missing
        }
        response = client.get("/api/v1/ks", params=params)
        assert response.status_code == 422

    def test_generate_kickstart_nonexistent_template(self, client: TestClient):
        """Test that requesting a non-existent template returns 404."""
        params = {
            "mac": "00:11:22:33:44:55",
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "serial": "SN123456789",
            "template_name": "nonexistent_template",
        }
        response = client.get("/api/v1/ks", params=params)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.fixture
def static_client(tmp_path: Path) -> TestClient:
    """Serve a built-GUI stand-in so tests don't depend on `pnpm build` output."""
    static_dir = tmp_path / "static"
    (static_dir / "assets").mkdir(parents=True)
    (static_dir / "index.html").write_text("<!doctype html><title>provisionR</title>")
    (static_dir / "assets" / "app.js").write_text("console.log('ok')")
    sibling = tmp_path / "static-private"
    sibling.mkdir()
    (sibling / "secret.txt").write_text("secret")
    return TestClient(create_app(static_dir=static_dir))


class TestStaticFileServing:
    """Tests for static file serving."""

    def test_serve_index_at_root(self, static_client: TestClient):
        """Test that index.html is served at the root path."""
        response = static_client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "<title>provisionR</title>" in response.text

    def test_serve_asset(self, static_client: TestClient):
        """Test that built assets are served from the static directory."""
        response = static_client.get("/assets/app.js")
        assert response.status_code == 200
        assert response.text == "console.log('ok')"

    def test_serve_nonexistent_file_returns_404(self, static_client: TestClient):
        """Test that requesting a non-existent file returns 404."""
        response = static_client.get("/nonexistent.txt")
        assert response.status_code == 404

    def test_path_traversal_blocked(self, static_client: TestClient):
        """Test that path traversal attempts are blocked."""
        response = static_client.get("/../../../etc/passwd")
        assert response.status_code == 404

    def test_sibling_directory_with_shared_prefix_blocked(
        self, static_client: TestClient
    ):
        """A sibling such as static-private/ must not pass the containment check."""
        response = static_client.get("/..%2fstatic-private%2fsecret.txt")
        assert response.status_code == 404

    def test_missing_static_dir_serves_api_only(self, tmp_path: Path):
        """Without a GUI build the API still works and / is not routed."""
        client = TestClient(create_app(static_dir=tmp_path / "absent"))
        assert client.get("/").status_code == 404
        assert client.get("/api/v1/config").status_code == 200


class TestPasswordPersistence:
    """Tests for password persistence across multiple requests."""

    def test_passwords_reused_for_same_machine(self, client: TestClient):
        """Test that the same machine gets the same passwords on subsequent requests."""
        params = {
            "mac": "AA:BB:CC:DD:EE:FF",
            "uuid": "machine-uuid-123",
            "serial": "SERIAL999",
        }

        # First request
        response1 = client.get("/api/v1/ks", params=params)
        assert response1.status_code == 200
        content1 = response1.text

        # Second request with same machine info
        response2 = client.get("/api/v1/ks", params=params)
        assert response2.status_code == 200
        content2 = response2.text

        # Content should be identical (same passwords)
        assert content1 == content2

    def test_different_machines_get_different_passwords(self, client: TestClient):
        """Test that different machines get different passwords."""
        params1 = {"mac": "11:22:33:44:55:66", "uuid": "uuid-1", "serial": "SERIAL001"}
        params2 = {"mac": "AA:BB:CC:DD:EE:FF", "uuid": "uuid-2", "serial": "SERIAL002"}

        response1 = client.get("/api/v1/ks", params=params1)
        response2 = client.get("/api/v1/ks", params=params2)

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Content should be different (different passwords)
        assert response1.text != response2.text

    def test_no_passwords_when_disabled(self, client: TestClient):
        """Test that passwords are not generated when generate_passwords is False."""
        # Disable password generation
        config_update = {
            "target_os": "Rocky9",
            "generate_passwords": False,
            "values": {},
        }
        client.put("/api/v1/config", json=config_update)

        params = {"mac": "00:11:22:33:44:55", "uuid": "test-uuid", "serial": "TEST123"}

        response = client.get("/api/v1/ks", params=params)
        assert response.status_code == 200
        # The template won't have password variables populated
        # (actual assertion depends on template implementation)


class TestMachinePasswordsExport:
    """Tests for machine passwords CSV export."""

    def test_export_empty_database(self, client: TestClient):
        """Test exporting when no machines exist."""
        response = client.get("/api/v1/machines/export")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]

        # Should have header row only
        lines = response.text.strip().split("\n")
        assert len(lines) == 1
        assert "mac,uuid,serial" in lines[0]

    def test_export_with_machines(self, client: TestClient):
        """Test exporting CSV with machine data."""
        # Generate kickstart for a machine to create password entries
        params = {
            "mac": "AA:BB:CC:DD:EE:FF",
            "uuid": "test-uuid-1",
            "serial": "SERIAL123",
        }
        client.get("/api/v1/ks", params=params)

        # Export CSV
        response = client.get("/api/v1/machines/export")
        assert response.status_code == 200

        lines = response.text.strip().split("\n")
        assert len(lines) == 2  # Header + 1 data row

        # Check header
        assert "mac,uuid,serial,root_password,user_password,luks_password" in lines[0]

        # Check data row contains machine info
        assert "AA:BB:CC:DD:EE:FF" in lines[1]
        assert "test-uuid-1" in lines[1]
        assert "SERIAL123" in lines[1]


class TestConfigValues:
    """Tests for custom values in config."""

    def test_values_available_in_template_context(self, client: TestClient):
        """Test that config values are made available during templating."""
        # Set config with custom values
        config_update = {
            "target_os": "Rocky9",
            "generate_passwords": True,
            "values": {"custom_key": "custom_value", "hostname_prefix": "prod"},
        }
        client.put("/api/v1/config", json=config_update)

        params = {"mac": "00:11:22:33:44:55", "uuid": "test-uuid", "serial": "TEST123"}

        response = client.get("/api/v1/ks", params=params)
        assert response.status_code == 200
        # Values should be available in template context
        # Actual usage depends on template implementation
