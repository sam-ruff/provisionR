"""Service for generating kickstart files."""

from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from provisionR.config import get_global_config_from_db
from provisionR.services.password_service import PasswordService
from provisionR.utils import PasswordHasher


class KickstartService:
    """Service for generating kickstart files from templates."""

    def __init__(
        self,
        db: Session,
        jinja_env: Optional[Environment] = None,
        password_service: Optional[PasswordService] = None,
    ):
        """
        Initialize the kickstart service.

        Args:
            db: Database session
            jinja_env: Optional Jinja2 environment (for testing)
            password_service: Optional password service (for testing)
        """
        self.db = db
        self.password_service = password_service or PasswordService(db)
        self.password_hasher = PasswordHasher()

        # Set up Jinja2 environment
        if jinja_env is None:
            templates_dir = Path(__file__).parent.parent / "templates"
            self.jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)))
        else:
            self.jinja_env = jinja_env

    def generate(
        self,
        mac: str,
        uuid: str,
        serial: str,
        template_name: str,
        query_params: Dict[str, Any],
    ) -> str:
        """
        Generate a kickstart file from a template.

        Args:
            mac: MAC address of the machine
            uuid: UUID of the machine
            serial: Serial number of the machine
            template_name: Name of the template to use (without .ks.j2 extension)
            query_params: Additional query parameters to pass to template

        Returns:
            Rendered kickstart file content

        Raises:
            TemplateNotFound: If the specified template doesn't exist
        """
        # Get config from database
        config = get_global_config_from_db(self.db)

        # Build template context from query parameters
        context = dict(query_params)

        # Ensure required fields are present
        context.update(
            {
                "mac": mac,
                "uuid": uuid,
                "serial": serial,
            }
        )

        # Add config values to context
        context.update(
            {
                "target_os": config.target_os.value,
            }
        )

        # Add custom values from config to context
        context.update(config.values)

        # Generate passwords if enabled
        if config.generate_passwords:
            root_pw, user_pw, luks_pw = self.password_service.get_or_create_passwords(
                mac, uuid, serial
            )

            # Hash passwords for use in kickstart (--iscrypted)
            context.update(
                {
                    "root_password": self.password_hasher.hash_sha512(root_pw),
                    "user_password": self.password_hasher.hash_sha512(user_pw),
                    "luks_password": self.password_hasher.hash_sha512(luks_pw),
                }
            )

        # Load and render the template
        template_file = f"{template_name}.ks.j2"
        template = self.jinja_env.get_template(template_file)
        rendered = template.render(**context)

        return rendered

    def generate_from_string(
        self,
        mac: str,
        uuid: str,
        serial: str,
        template_string: str,
        query_params: Dict[str, Any],
    ) -> str:
        """
        Generate a kickstart file from a template string (useful for testing).

        Args:
            mac: MAC address of the machine
            uuid: UUID of the machine
            serial: Serial number of the machine
            template_string: Template content as a string
            query_params: Additional query parameters to pass to template

        Returns:
            Rendered kickstart file content
        """
        # Get config from database
        config = get_global_config_from_db(self.db)

        # Build template context from query parameters
        context = dict(query_params)

        # Ensure required fields are present
        context.update(
            {
                "mac": mac,
                "uuid": uuid,
                "serial": serial,
            }
        )

        # Add config values to context
        context.update(
            {
                "target_os": config.target_os.value,
            }
        )

        # Add custom values from config to context
        context.update(config.values)

        # Generate passwords if enabled
        if config.generate_passwords:
            root_pw, user_pw, luks_pw = self.password_service.get_or_create_passwords(
                mac, uuid, serial
            )

            # Hash passwords for use in kickstart (--iscrypted)
            context.update(
                {
                    "root_password": self.password_hasher.hash_sha512(root_pw),
                    "user_password": self.password_hasher.hash_sha512(user_pw),
                    "luks_password": self.password_hasher.hash_sha512(luks_pw),
                }
            )

        # Render the template string
        template = self.jinja_env.from_string(template_string)
        rendered = template.render(**context)

        return rendered
