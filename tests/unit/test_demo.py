"""Unit tests for the read-only demo mode rules."""

import pytest

from provisionR.demo import demo_mode_from_environment, is_refused


@pytest.mark.parametrize("value", ["true", "TRUE", "1", "yes", "on", " true "])
def test_demo_mode_is_on_for_truthy_values(value):
    assert demo_mode_from_environment({"PROVISIONR_DEMO_MODE": value}) is True


@pytest.mark.parametrize("value", ["", "false", "0", "no", "off", "demo"])
def test_demo_mode_is_off_otherwise(value):
    assert demo_mode_from_environment({"PROVISIONR_DEMO_MODE": value}) is False


def test_demo_mode_is_off_when_unset():
    assert demo_mode_from_environment({}) is False


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE", "OPTIONS", "put"])
def test_every_non_read_method_is_refused(method):
    assert is_refused(method, "/api/v1/config")


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/ks",
        "/api/v1/ks/",
        "/api/v1/machines/export",
        "//api/v1/ks",
        "/api//v1/machines/export",
    ],
)
def test_machine_creation_and_export_are_refused_even_for_get(path):
    assert is_refused("GET", path)
    assert is_refused("HEAD", path)


@pytest.mark.parametrize(
    "path",
    [
        "/",
        "/assets/index.js",
        "/api/health",
        "/api/v1/config",
        "/api/v1/templates/default",
        "/docs",
    ],
)
def test_reads_are_allowed(path):
    assert not is_refused("GET", path)
    assert not is_refused("HEAD", path)
