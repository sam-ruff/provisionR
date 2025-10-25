"""Password hashing utilities for kickstart files."""
import secrets
import string
from passlib.hash import sha512_crypt


class PasswordHasher:
    """Hashes passwords for use in kickstart files."""

    @staticmethod
    def hash_sha512(password: str) -> str:
        """
        Hash a password using SHA-512 (suitable for --iscrypted in kickstart files).

        Args:
            password: Plain text password to hash

        Returns:
            SHA-512 hashed password suitable for kickstart files
        """
        # Generate a random salt
        salt_chars = string.ascii_letters + string.digits + './'
        salt = ''.join(secrets.choice(salt_chars) for _ in range(16))

        # Hash the password with the salt using SHA-512
        hashed = sha512_crypt.using(salt=salt, rounds=5000).hash(password)

        return hashed
