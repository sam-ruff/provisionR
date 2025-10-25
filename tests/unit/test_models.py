"""Unit tests for models."""
import pytest
from pydantic import ValidationError
from provisionR.models import GlobalConfig, TargetOS


class TestTargetOS:
    """Tests for TargetOS enum."""

    def test_target_os_values(self):
        """Test that TargetOS enum has expected values."""
        assert TargetOS.ROCKY9.value == "Rocky9"
        assert TargetOS.UBUNTU2504.value == "Ubuntu25.04"


class TestGlobalConfig:
    """Tests for GlobalConfig model."""

    def test_default_config(self):
        """Test creating a GlobalConfig with defaults."""
        config = GlobalConfig()
        assert config.target_os == TargetOS.ROCKY9
        assert config.generate_passwords is True
        assert config.values == {}

    def test_custom_config(self):
        """Test creating a GlobalConfig with custom values."""
        config = GlobalConfig(
            target_os=TargetOS.UBUNTU2504,
            generate_passwords=False,
            values={"key1": "value1", "key2": ["list", "of", "items"]}
        )
        assert config.target_os == TargetOS.UBUNTU2504
        assert config.generate_passwords is False
        assert config.values["key1"] == "value1"
        assert len(config.values["key2"]) == 3

    def test_invalid_target_os(self):
        """Test that invalid target_os raises validation error."""
        with pytest.raises(ValidationError):
            GlobalConfig(target_os="InvalidOS")
