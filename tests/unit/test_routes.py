"""Unit tests for route registration and the generated OpenAPI schema."""

from pathlib import Path

from fastapi.routing import APIRoute

from provisionR.app import create_app
from provisionR.routes import api_router


def _openapi(tmp_path: Path) -> dict:
    """Build the schema for an app that also serves a static GUI build."""
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    (static_dir / "index.html").write_text("<!doctype html>")
    return create_app(demo_mode=False, static_dir=static_dir).openapi()


def _refs(node) -> list[str]:
    """Collect every $ref in a schema fragment."""
    if isinstance(node, dict):
        found = [node["$ref"]] if isinstance(node.get("$ref"), str) else []
        return found + [ref for value in node.values() for ref in _refs(value)]
    if isinstance(node, list):
        return [ref for item in node for ref in _refs(item)]
    return []


class TestOpenAPISchema:
    """Guard schema generation across FastAPI upgrades."""

    def test_every_api_route_is_documented(self, tmp_path: Path):
        """Each API route appears under /api with its HTTP methods."""
        paths = _openapi(tmp_path)["paths"]
        for route in api_router.routes:
            assert isinstance(route, APIRoute)
            operations = paths[f"/api{route.path}"]
            for method in route.methods:
                assert method.lower() in operations

    def test_static_routes_are_hidden(self, tmp_path: Path):
        """The GUI index and catch-all file routes stay out of the schema."""
        paths = _openapi(tmp_path)["paths"]
        assert "/" not in paths
        assert "/{full_path}" not in paths
        assert all(path.startswith("/api/") for path in paths)

    def test_config_response_model_is_published(self, tmp_path: Path):
        """GET /api/v1/config documents the GlobalConfig response model."""
        schema = _openapi(tmp_path)
        response = schema["paths"]["/api/v1/config"]["get"]["responses"]["200"]
        ref = response["content"]["application/json"]["schema"]["$ref"]
        assert ref == "#/components/schemas/GlobalConfig"
        properties = schema["components"]["schemas"]["GlobalConfig"]["properties"]
        assert {"target_os", "generate_passwords", "values"} <= properties.keys()

    def test_all_schema_references_resolve(self, tmp_path: Path):
        """Every $ref points at a component that exists in the schema."""
        schema = _openapi(tmp_path)
        components = schema["components"]["schemas"]
        refs = _refs(schema["paths"]) + _refs(components)
        assert refs
        prefix = "#/components/schemas/"
        for ref in refs:
            assert ref.startswith(prefix)
            assert ref.removeprefix(prefix) in components
