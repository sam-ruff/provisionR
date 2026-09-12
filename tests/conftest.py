"""Pytest configuration and fixtures."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from fastapi.testclient import TestClient

test_storage = TemporaryDirectory(prefix="provisionr-tests-")
os.environ["PROVISIONR_TEST_MODE"] = "false"
os.environ["PROVISIONR_DB_PATH"] = str(Path(test_storage.name) / "test.db")
os.environ["PROVISIONR_TEMPLATE_DIR"] = str(Path(test_storage.name) / "templates")


@pytest.fixture(scope="session", autouse=True)
def isolated_storage():
    """Keep tests away from checkout databases and bundled templates."""
    yield
    from provisionR.database import engine

    engine.dispose()
    test_storage.cleanup()


@pytest.fixture(autouse=True)
def reset_database():
    """Reset the in-memory database before each test."""
    # Import after setting test mode
    from provisionR.database import Base, engine

    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    # Recreate all tables
    Base.metadata.create_all(bind=engine)

    yield

    # Clean up after test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from provisionR.app import create_app

    app = create_app()
    return TestClient(app)
