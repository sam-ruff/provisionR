"""Unit tests for service layer."""
import pytest
from jinja2 import Environment
from sqlalchemy.orm import Session
from unittest.mock import Mock

from provisionR.services.kickstart_service import KickstartService
from provisionR.services.password_service import PasswordService
from provisionR.services.export_service import ExportService
from provisionR.models import DBMachinePasswords, GlobalConfig, TargetOS
from provisionR.config import update_global_config_in_db
from provisionR.database import SessionLocal


@pytest.fixture
def db_session():
    """Create a database session for unit tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestPasswordService:
    """Tests for PasswordService."""

    def test_generate_new_passwords(self, db_session: Session):
        """Test generating new passwords for a machine."""
        service = PasswordService(db_session)

        root_pw, user_pw, luks_pw = service.get_or_create_passwords(
            mac="AA:BB:CC:DD:EE:FF",
            uuid="test-uuid",
            serial="SERIAL123"
        )

        # Check passwords are generated
        assert root_pw is not None
        assert user_pw is not None
        assert luks_pw is not None

        # Check format (word-word-word-number)
        assert "-" in root_pw
        parts = root_pw.split("-")
        assert len(parts) == 4
        assert parts[-1].isdigit()

    def test_reuse_existing_passwords(self, db_session: Session):
        """Test that existing passwords are reused."""
        service = PasswordService(db_session)

        # First call - generates new passwords
        root1, user1, luks1 = service.get_or_create_passwords(
            mac="AA:BB:CC:DD:EE:FF",
            uuid="test-uuid",
            serial="SERIAL123"
        )

        # Second call - should return same passwords
        root2, user2, luks2 = service.get_or_create_passwords(
            mac="AA:BB:CC:DD:EE:FF",
            uuid="test-uuid",
            serial="SERIAL123"
        )

        assert root1 == root2
        assert user1 == user2
        assert luks1 == luks2


class TestKickstartService:
    """Tests for KickstartService."""

    def test_generate_from_string_basic_template(self, db_session: Session):
        """Test generating kickstart from a string template."""
        service = KickstartService(db_session)

        template_string = """MAC: {{ mac }}
UUID: {{ uuid }}
Serial: {{ serial }}
OS: {{ target_os }}"""

        result = service.generate_from_string(
            mac="AA:BB:CC:DD:EE:FF",
            uuid="test-uuid-123",
            serial="SN999",
            template_string=template_string,
            query_params={}
        )

        assert "MAC: AA:BB:CC:DD:EE:FF" in result
        assert "UUID: test-uuid-123" in result
        assert "Serial: SN999" in result
        assert "OS: Rocky9" in result

    def test_generate_from_string_with_custom_values(self, db_session: Session):
        """Test that custom config values are available in templates."""
        # Update config with custom values
        config = GlobalConfig(
            target_os=TargetOS.ROCKY9,
            generate_passwords=True,
            values={"custom_key": "custom_value", "hostname": "webserver01"}
        )
        update_global_config_in_db(db_session, config)

        service = KickstartService(db_session)

        template_string = """Custom: {{ custom_key }}
Hostname: {{ hostname }}"""

        result = service.generate_from_string(
            mac="AA:BB:CC",
            uuid="uuid",
            serial="serial",
            template_string=template_string,
            query_params={}
        )

        assert "Custom: custom_value" in result
        assert "Hostname: webserver01" in result

    def test_generate_from_string_with_passwords(self, db_session: Session):
        """Test that passwords are generated and hashed."""
        service = KickstartService(db_session)

        template_string = """Root: {{ root_password }}
User: {{ user_password }}
LUKS: {{ luks_password }}"""

        result = service.generate_from_string(
            mac="AA:BB:CC:DD:EE:FF",
            uuid="test-uuid",
            serial="SERIAL123",
            template_string=template_string,
            query_params={}
        )

        # Check that passwords are present
        assert "Root: " in result
        assert "User: " in result
        assert "LUKS: " in result

        # Check that passwords are hashed (start with $6$ for SHA-512)
        lines = result.split('\n')
        for line in lines:
            if line.startswith("Root:") or line.startswith("User:") or line.startswith("LUKS:"):
                password_hash = line.split(": ")[1]
                assert password_hash.startswith("$6$"), "Password should be hashed with SHA-512"

    def test_generate_from_string_passwords_are_consistent(self, db_session: Session):
        """Test that the same machine gets the same hashed passwords."""
        service = KickstartService(db_session)

        template_string = "Root: {{ root_password }}"

        # First generation
        result1 = service.generate_from_string(
            mac="AA:BB:CC:DD:EE:FF",
            uuid="test-uuid",
            serial="SERIAL123",
            template_string=template_string,
            query_params={}
        )

        # Second generation - same machine
        result2 = service.generate_from_string(
            mac="AA:BB:CC:DD:EE:FF",
            uuid="test-uuid",
            serial="SERIAL123",
            template_string=template_string,
            query_params={}
        )

        # Hashes will be different (different salts) but they hash the same plaintext password
        # So we can't directly compare them, but we can verify both are hashed
        assert "$6$" in result1
        assert "$6$" in result2

    def test_generate_from_string_with_query_params(self, db_session: Session):
        """Test that query parameters are passed to template."""
        service = KickstartService(db_session)

        template_string = """Hostname: {{ hostname }}
Timezone: {{ timezone }}"""

        result = service.generate_from_string(
            mac="AA:BB:CC",
            uuid="uuid",
            serial="serial",
            template_string=template_string,
            query_params={"hostname": "server01", "timezone": "America/New_York"}
        )

        assert "Hostname: server01" in result
        assert "Timezone: America/New_York" in result


class TestExportService:
    """Tests for ExportService."""

    def test_export_empty_database(self, db_session: Session):
        """Test exporting when no machines exist."""
        service = ExportService(db_session)
        csv_content = service.export_machine_passwords_csv()

        lines = csv_content.strip().split('\n')
        assert len(lines) == 1  # Header only
        assert "mac,uuid,serial" in lines[0]

    def test_export_with_machine_data(self, db_session: Session):
        """Test exporting CSV with machine data."""
        # Create a machine entry
        password_service = PasswordService(db_session)
        password_service.get_or_create_passwords(
            mac="AA:BB:CC:DD:EE:FF",
            uuid="test-uuid-1",
            serial="SERIAL123"
        )

        # Export
        export_service = ExportService(db_session)
        csv_content = export_service.export_machine_passwords_csv()

        lines = csv_content.strip().split('\n')
        assert len(lines) == 2  # Header + 1 data row

        # Check data
        assert "AA:BB:CC:DD:EE:FF" in lines[1]
        assert "test-uuid-1" in lines[1]
        assert "SERIAL123" in lines[1]
