"""Service for exporting data."""

import csv
import io
from sqlalchemy.orm import Session
from provisionR.models import DBMachinePasswords


class ExportService:
    """Service for exporting data to various formats."""

    def __init__(self, db: Session):
        """Initialize the export service with a database session."""
        self.db = db

    def export_machine_passwords_csv(self) -> str:
        """
        Export all machine passwords as CSV content.

        Returns:
            CSV content as a string
        """
        # Query all machines ordered by creation date
        machines = (
            self.db.query(DBMachinePasswords)
            .order_by(DBMachinePasswords.created_at)
            .all()
        )

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "mac",
                "uuid",
                "serial",
                "root_password",
                "user_password",
                "luks_password",
                "created_at",
            ]
        )

        # Write data rows
        for machine in machines:
            writer.writerow(
                [
                    machine.mac,
                    machine.uuid,
                    machine.serial,
                    machine.root_password,
                    machine.user_password,
                    machine.luks_password,
                    machine.created_at.isoformat() if machine.created_at else "",
                ]
            )

        # Return CSV content
        output.seek(0)
        return output.getvalue()
