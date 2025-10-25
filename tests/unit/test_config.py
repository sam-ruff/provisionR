"""Unit tests for configuration management."""

import pytest
from sqlalchemy.orm import Session
from provisionR.config import get_global_config_from_db, update_global_config_in_db
from provisionR.models import GlobalConfig, TargetOS
from provisionR.database import SessionLocal


@pytest.fixture
def db_session():
    """Create a database session for unit tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestConfigFunctions:
    """Tests for config database functions."""

    def test_get_default_config(self, db_session: Session):
        """Test that getting config returns defaults when none exists."""
        config = get_global_config_from_db(db_session)
        assert config.target_os == TargetOS.ROCKY9
        assert config.generate_passwords is True
        assert config.values == {}

    def test_update_config(self, db_session: Session):
        """Test updating the configuration."""
        new_config = GlobalConfig(
            target_os=TargetOS.UBUNTU2504,
            generate_passwords=False,
            values={"custom_key": "custom_value"},
        )
        updated = update_global_config_in_db(db_session, new_config)

        assert updated.target_os == TargetOS.UBUNTU2504
        assert updated.generate_passwords is False
        assert updated.values["custom_key"] == "custom_value"

    def test_config_persists(self, db_session: Session):
        """Test that configuration changes persist across reads."""
        # Update config
        new_config = GlobalConfig(
            target_os=TargetOS.UBUNTU2504,
            generate_passwords=False,
            values={"test": "value"},
        )
        update_global_config_in_db(db_session, new_config)

        # Read it back
        retrieved_config = get_global_config_from_db(db_session)
        assert retrieved_config.target_os == TargetOS.UBUNTU2504
        assert retrieved_config.generate_passwords is False
        assert retrieved_config.values["test"] == "value"
