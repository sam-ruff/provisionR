import pytest

from provisionR.template_storage import (
    BUNDLED_TEMPLATES,
    template_search_paths,
    writable_template_directory,
)


def test_unconfigured_directory_preserves_bundled_behaviour(monkeypatch):
    monkeypatch.delenv("PROVISIONR_TEMPLATE_DIR", raising=False)
    assert writable_template_directory() == BUNDLED_TEMPLATES
    assert template_search_paths() == [BUNDLED_TEMPLATES]


def test_configured_directory_precedes_bundled_defaults(monkeypatch, tmp_path):
    monkeypatch.setenv("PROVISIONR_TEMPLATE_DIR", str(tmp_path))
    assert writable_template_directory() == tmp_path
    assert template_search_paths() == [tmp_path, BUNDLED_TEMPLATES]


def test_empty_setting_fails_closed(monkeypatch):
    monkeypatch.setenv("PROVISIONR_TEMPLATE_DIR", " ")
    with pytest.raises(ValueError, match="must not be empty"):
        writable_template_directory()
