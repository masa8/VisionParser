"""Environment variable management class"""

import os
from dotenv import load_dotenv


class EnvConfigError(Exception):
    """Base class for environment variable configuration errors"""

    pass


class OpenAIKeyNotFoundError(EnvConfigError):
    """OpenAI API key not found"""

    def __init__(self):
        super().__init__(
            "OPENAI_API_KEY is not set.\n"
            "Please create a .env file and configure it as follows:\n"
            "OPENAI_API_KEY=sk-..."
        )


class OpenAIKeyInvalidError(EnvConfigError):
    """OpenAI API key is invalid"""

    def __init__(self):
        super().__init__(
            "OPENAI_API_KEY is invalid.\nPlease check the API key in your .env file."
        )


class EnvConfig:
    """Class for managing environment variables"""

    def __init__(self, env_file: str = ".env"):
        """
        Initialize environment variable configuration

        Args:
            env_file: Path to .env file (default: .env)
        """
        self.env_file = env_file
        self._load_env()

    def _load_env(self) -> None:
        """Load environment variables"""
        load_dotenv(self.env_file)

    def get(self, key: str, default: str = None) -> str:
        """
        Get environment variable

        Args:
            key: Environment variable key
            default: Default value

        Returns:
            Environment variable value
        """
        return os.environ.get(key, default)

    def get_openai_api_key(self) -> str:
        """
        Get and validate OpenAI API key

        Returns:
            API key

        Raises:
            OpenAIKeyNotFoundError: API key is not set
            OpenAIKeyInvalidError: API key is invalid
        """
        api_key = self.get("OPENAI_API_KEY")

        if not api_key:
            raise OpenAIKeyNotFoundError()

        # Check for placeholder
        if api_key == "your-api-key-here":
            raise OpenAIKeyInvalidError()

        # Basic format check (starts with sk-)
        if not api_key.startswith("sk-"):
            raise OpenAIKeyInvalidError()

        return api_key

    def __repr__(self) -> str:
        """String representation of configuration"""
        return f"EnvConfig(env_file={self.env_file})"
