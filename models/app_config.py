"""Class for integrated management of application configuration"""

from pathlib import Path

from models.env_config import EnvConfig
from models.image_folder_config import ImageFolderConfig
from models.openai_config import OpenAIConfig


class Config:
    """Class for integrated management of application-wide configuration (Facade pattern)"""

    def __init__(
        self,
        env_file: str = ".env",
        images_folder: str | Path = "images",
        output_file: str = "extracted_data_gpt_all.csv",
        extract_fields: list[str] = None,
    ):
        """
        Initialize configuration

        Args:
            env_file: Path to .env file (default: .env)
            images_folder: Path to image folder (default: images)
            output_file: Output filename (default: extracted_data_gpt_all.csv)
            extract_fields: List of fields to extract (default: ["filename", "email", "firstname", "name"])
        """
        # Model configuration (delegation)
        self.env = EnvConfig(env_file)
        self.images = ImageFolderConfig(images_folder)
        self.openai = OpenAIConfig(self.env.get_openai_api_key())

        # Application-specific configuration
        self.output_file = output_file
        self.extract_fields = extract_fields or [
            "filename",
            "email",
            "firstname",
            "name",
        ]

    def validate(self) -> None:
        """
        Validate all configurations

        Raises:
            OpenAIKeyNotFoundError: API key is not set
            OpenAIKeyInvalidError: API key is invalid
            ImageFolderNotFoundError: Image folder not found
        """
        # API key validation (already executed during initialization)
        _ = self.openai.api_key
        # Image folder validation
        self.images.validate()

    def __repr__(self) -> str:
        """String representation of configuration"""
        return (
            f"Config(\n"
            f"  env: {self.env},\n"
            f"  images: {self.images},\n"
            f"  openai: {self.openai},\n"
            f"  output_file: {self.output_file},\n"
            f"  extract_fields: {self.extract_fields}\n"
            f")"
        )
