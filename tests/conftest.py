"""Pytest configuration and fixtures."""

import os
import pytest
from fastapi.testclient import TestClient
from provisionR.app import create_app


@pytest.fixture(scope="session", autouse=True)
def set_test_mode():
    """Set test mode environment variable for all tests."""
    os.environ["PROVISIONR_TEST_MODE"] = "true"
    yield
    os.environ.pop("PROVISIONR_TEST_MODE", None)


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
    app = create_app()
    return TestClient(app)
