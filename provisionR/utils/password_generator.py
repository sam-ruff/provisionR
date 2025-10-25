"""Password generation utilities."""
import secrets
import petname


class PasswordGenerator:
    """Generates secure random passphrases using petnames."""

    @staticmethod
    def generate_passphrase() -> str:
        """
        Generate a secure random passphrase in the format: word-word-word-###

        Returns:
            A secure random passphrase (e.g., "happy-red-tiger-42")
        """
        # Generate 3 random words
        words = petname.generate(words=3, separator="-")

        # Generate 1-3 digit number (10-999)
        number = secrets.randbelow(990) + 10

        return f"{words}-{number}"
