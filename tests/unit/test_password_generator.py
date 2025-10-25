"""Unit tests for password generator."""
import pytest
import re
from provisionR.utils import PasswordGenerator


class TestPasswordGenerator:
    """Tests for the PasswordGenerator class."""

    def test_generate_passphrase_format(self):
        """Test that passphrase follows the word-word-word-### format."""
        passphrase = PasswordGenerator.generate_passphrase()

        # Should match pattern: word-word-word-number
        # Number should be 2-3 digits (10-999)
        pattern = r'^[a-z]+-[a-z]+-[a-z]+-\d{2,3}$'
        assert re.match(pattern, passphrase), f"Passphrase '{passphrase}' doesn't match expected format"

    def test_generate_passphrase_has_hyphen_separators(self):
        """Test that passphrase uses hyphens as separators."""
        passphrase = PasswordGenerator.generate_passphrase()
        parts = passphrase.split('-')
        assert len(parts) == 4, "Passphrase should have 4 parts (3 words + 1 number)"

    def test_generate_passphrase_number_range(self):
        """Test that the number suffix is in the correct range (10-999)."""
        passphrase = PasswordGenerator.generate_passphrase()
        parts = passphrase.split('-')
        number = int(parts[-1])
        assert 10 <= number <= 999, f"Number {number} should be between 10 and 999"

    def test_passphrases_are_unique(self):
        """Test that multiple generated passphrases are different."""
        passphrases = [PasswordGenerator.generate_passphrase() for _ in range(20)]
        # Most should be unique (unlikely to get duplicates with large word pool)
        unique_count = len(set(passphrases))
        assert unique_count > 15, "Most passphrases should be unique"

    def test_passphrase_is_lowercase(self):
        """Test that passphrase words are lowercase."""
        passphrase = PasswordGenerator.generate_passphrase()
        # Remove the number suffix and check words
        words_part = '-'.join(passphrase.split('-')[:-1])
        assert words_part.islower(), "Words should be lowercase"
