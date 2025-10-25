"""Unit tests for password hasher."""
import pytest
from provisionR.utils import PasswordHasher


class TestPasswordHasher:
    """Tests for the PasswordHasher class."""

    def test_hash_sha512_format(self):
        """Test that hash_sha512 returns a properly formatted SHA-512 hash."""
        hasher = PasswordHasher()
        password = "test-password-123"

        hashed = hasher.hash_sha512(password)

        # SHA-512 hashes start with $6$
        assert hashed.startswith("$6$")

        # Hash should be fairly long
        assert len(hashed) > 50

    def test_hash_sha512_different_salts(self):
        """Test that the same password produces different hashes (different salts)."""
        hasher = PasswordHasher()
        password = "same-password"

        hash1 = hasher.hash_sha512(password)
        hash2 = hasher.hash_sha512(password)

        # Hashes should be different due to different salts
        assert hash1 != hash2

        # But both should be valid SHA-512 hashes
        assert hash1.startswith("$6$")
        assert hash2.startswith("$6$")

    def test_hash_sha512_different_passwords(self):
        """Test that different passwords produce different hashes."""
        hasher = PasswordHasher()

        hash1 = hasher.hash_sha512("password1")
        hash2 = hasher.hash_sha512("password2")

        assert hash1 != hash2
        assert hash1.startswith("$6$")
        assert hash2.startswith("$6$")

    def test_hash_sha512_with_special_characters(self):
        """Test hashing passwords with special characters."""
        hasher = PasswordHasher()
        password = "p@ssw0rd!#$%^&*()"

        hashed = hasher.hash_sha512(password)

        assert hashed.startswith("$6$")
        assert len(hashed) > 50
