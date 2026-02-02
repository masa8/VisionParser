"""OpenAI API configuration management class"""


class OpenAIConfigError(Exception):
    """Base class for OpenAI configuration errors"""

    pass


class InvalidMaxTokensError(OpenAIConfigError):
    """Invalid max_tokens value"""

    def __init__(self, value: int):
        super().__init__(f"max_tokens must be a positive integer: {value}")


class InvalidTemperatureError(OpenAIConfigError):
    """Invalid temperature value"""

    def __init__(self, value: float):
        super().__init__(f"temperature must be in the range 0.0 to 2.0: {value}")


class OpenAIConfig:
    """Class for managing OpenAI API configuration"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        max_tokens: int = 2000,
        temperature: float = 0.0,
    ):
        """
        Initialize OpenAI API configuration

        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4o)
            max_tokens: Maximum number of tokens (default: 2000)
            temperature: Temperature value (default: 0.0)
        """
        self._api_key = api_key
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature

    @property
    def api_key(self) -> str:
        """Get API key"""
        return self._api_key

    @property
    def model(self) -> str:
        """Get model to use"""
        return self._model

    @model.setter
    def model(self, value: str) -> None:
        """Set model to use"""
        self._model = value

    @property
    def max_tokens(self) -> int:
        """Get maximum number of tokens"""
        return self._max_tokens

    @max_tokens.setter
    def max_tokens(self, value: int) -> None:
        """Set maximum number of tokens"""
        if value <= 0:
            raise InvalidMaxTokensError(value)
        self._max_tokens = value

    @property
    def temperature(self) -> float:
        """Get temperature value"""
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        """Set temperature value"""
        if not 0.0 <= value <= 2.0:
            raise InvalidTemperatureError(value)
        self._temperature = value

    def get_api_key_masked(self) -> str:
        """
        Get masked API key (for display)

        Returns:
            Masked API key (e.g., ***l2AA)
        """
        if len(self._api_key) > 4:
            return "***" + self._api_key[-4:]
        return "***"

    def __repr__(self) -> str:
        """String representation of configuration"""
        return (
            f"OpenAIConfig(\n"
            f"  api_key={self.get_api_key_masked()},\n"
            f"  model={self.model},\n"
            f"  max_tokens={self.max_tokens},\n"
            f"  temperature={self.temperature}\n"
            f")"
        )
