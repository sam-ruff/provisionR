"""Service for managing machine passwords."""
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from provisionR.models import DBMachinePasswords
from provisionR.utils import PasswordGenerator


class PasswordService:
    """Service for generating and retrieving machine passwords."""

    def __init__(self, db: Session):
        """Initialize the password service with a database session."""
        self.db = db
        self.password_gen = PasswordGenerator()

    def get_or_create_passwords(
        self, mac: str, uuid: str, serial: str
    ) -> Tuple[str, str, str]:
        """
        Get existing passwords for a machine or generate new ones.

        Args:
            mac: MAC address of the machine
            uuid: UUID of the machine
            serial: Serial number of the machine

        Returns:
            Tuple of (root_password, user_password, luks_password)
        """
        # Check if we've seen this machine before
        existing_machine = self.db.query(DBMachinePasswords).filter(
            DBMachinePasswords.mac == mac,
            DBMachinePasswords.uuid == uuid,
            DBMachinePasswords.serial == serial
        ).first()

        if existing_machine:
            # Reuse existing passwords
            return (
                existing_machine.root_password,
                existing_machine.user_password,
                existing_machine.luks_password,
            )
        else:
            # Generate new passwords
            root_pw = self.password_gen.generate_passphrase()
            user_pw = self.password_gen.generate_passphrase()
            luks_pw = self.password_gen.generate_passphrase()

            # Store passwords in database
            new_machine = DBMachinePasswords(
                mac=mac,
                uuid=uuid,
                serial=serial,
                root_password=root_pw,
                user_password=user_pw,
                luks_password=luks_pw,
            )
            self.db.add(new_machine)
            self.db.commit()

            return root_pw, user_pw, luks_pw
