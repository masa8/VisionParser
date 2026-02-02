"""Tests for models package"""

import pytest
from pathlib import Path
from models.env_config import (
    EnvConfig,
    OpenAIKeyNotFoundError,
    OpenAIKeyInvalidError,
)
from models.image_folder_config import (
    ImageFolderConfig,
    ImageFolderNotFoundError,
    NoImageFilesError,
)
from models.openai_config import (
    OpenAIConfig,
    InvalidMaxTokensError,
    InvalidTemperatureError,
)
from models.app_config import Config


class TestEnvConfig:
    """Test cases for EnvConfig"""

    def test_env_config_initialization(self, tmp_path):
        """Test EnvConfig initialization"""
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_KEY=test_value\n")

        config = EnvConfig(str(env_file))
        assert config.env_file == str(env_file)

    def test_get_existing_key(self, tmp_path, monkeypatch):
        """Test getting existing environment variable"""
        monkeypatch.setenv("TEST_KEY", "test_value")
        config = EnvConfig()
        assert config.get("TEST_KEY") == "test_value"

    def test_get_missing_key_with_default(self):
        """Test getting missing key with default value"""
        config = EnvConfig()
        assert config.get("NONEXISTENT_KEY", "default") == "default"

    def test_get_openai_api_key_not_found(self, monkeypatch, tmp_path):
        """Test OpenAI API key not found error"""
        # Create a temporary .env file without the key
        env_file = tmp_path / ".env"
        env_file.write_text("")

        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        config = EnvConfig(str(env_file))
        with pytest.raises(OpenAIKeyNotFoundError):
            config.get_openai_api_key()

    def test_get_openai_api_key_invalid_placeholder(self, monkeypatch):
        """Test OpenAI API key with placeholder"""
        monkeypatch.setenv("OPENAI_API_KEY", "your-api-key-here")
        config = EnvConfig()
        with pytest.raises(OpenAIKeyInvalidError):
            config.get_openai_api_key()

    def test_get_openai_api_key_invalid_format(self, monkeypatch):
        """Test OpenAI API key with invalid format"""
        monkeypatch.setenv("OPENAI_API_KEY", "invalid-key")
        config = EnvConfig()
        with pytest.raises(OpenAIKeyInvalidError):
            config.get_openai_api_key()

    def test_get_openai_api_key_valid(self, monkeypatch):
        """Test valid OpenAI API key"""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test123456")
        config = EnvConfig()
        assert config.get_openai_api_key() == "sk-test123456"


class TestImageFolderConfig:
    """Test cases for ImageFolderConfig"""

    def test_initialization(self):
        """Test ImageFolderConfig initialization"""
        config = ImageFolderConfig("test_images")
        assert config.folder_path == Path("test_images")

    def test_folder_path_property(self):
        """Test folder_path property getter and setter"""
        config = ImageFolderConfig()
        assert config.folder_path == Path("images")

        config.folder_path = "new_folder"
        assert config.folder_path == Path("new_folder")

    def test_validate_folder_not_found(self, tmp_path):
        """Test validation with non-existent folder"""
        config = ImageFolderConfig(tmp_path / "nonexistent")
        with pytest.raises(ImageFolderNotFoundError):
            config.validate()

    def test_validate_folder_exists(self, tmp_path):
        """Test validation with existing folder"""
        config = ImageFolderConfig(tmp_path)
        config.validate()  # Should not raise

    def test_get_image_files_no_images(self, tmp_path):
        """Test getting image files from empty folder"""
        config = ImageFolderConfig(tmp_path)
        with pytest.raises(NoImageFilesError):
            config.get_image_files()

    def test_get_image_files_with_images(self, tmp_path):
        """Test getting image files from folder with images"""
        # Create test image files
        (tmp_path / "test1.png").touch()
        (tmp_path / "test2.jpg").touch()
        (tmp_path / "test3.txt").touch()  # Non-image file

        config = ImageFolderConfig(tmp_path)
        files = config.get_image_files()

        assert len(files) == 2
        assert all(f.suffix.lower() in [".png", ".jpg"] for f in files)

    def test_supported_extensions(self):
        """Test supported image extensions"""
        assert ".png" in ImageFolderConfig.SUPPORTED_EXTENSIONS
        assert ".jpg" in ImageFolderConfig.SUPPORTED_EXTENSIONS
        assert ".jpeg" in ImageFolderConfig.SUPPORTED_EXTENSIONS


class TestOpenAIConfig:
    """Test cases for OpenAIConfig"""

    def test_initialization(self):
        """Test OpenAIConfig initialization"""
        config = OpenAIConfig(api_key="sk-test123")
        assert config.api_key == "sk-test123"
        assert config.model == "gpt-4o"
        assert config.max_tokens == 2000
        assert config.temperature == 0.0

    def test_custom_parameters(self):
        """Test initialization with custom parameters"""
        config = OpenAIConfig(
            api_key="sk-test123",
            model="gpt-4-turbo",
            max_tokens=1000,
            temperature=0.5,
        )
        assert config.model == "gpt-4-turbo"
        assert config.max_tokens == 1000
        assert config.temperature == 0.5

    def test_model_setter(self):
        """Test model property setter"""
        config = OpenAIConfig(api_key="sk-test123")
        config.model = "gpt-3.5-turbo"
        assert config.model == "gpt-3.5-turbo"

    def test_max_tokens_setter_valid(self):
        """Test max_tokens setter with valid value"""
        config = OpenAIConfig(api_key="sk-test123")
        config.max_tokens = 500
        assert config.max_tokens == 500

    def test_max_tokens_setter_invalid(self):
        """Test max_tokens setter with invalid value"""
        config = OpenAIConfig(api_key="sk-test123")
        with pytest.raises(InvalidMaxTokensError):
            config.max_tokens = 0
        with pytest.raises(InvalidMaxTokensError):
            config.max_tokens = -100

    def test_temperature_setter_valid(self):
        """Test temperature setter with valid value"""
        config = OpenAIConfig(api_key="sk-test123")
        config.temperature = 1.0
        assert config.temperature == 1.0

    def test_temperature_setter_invalid(self):
        """Test temperature setter with invalid value"""
        config = OpenAIConfig(api_key="sk-test123")
        with pytest.raises(InvalidTemperatureError):
            config.temperature = -0.1
        with pytest.raises(InvalidTemperatureError):
            config.temperature = 2.1

    def test_get_api_key_masked(self):
        """Test masked API key"""
        config = OpenAIConfig(api_key="sk-test123456")
        masked = config.get_api_key_masked()
        assert masked == "***3456"
        assert "sk-test" not in masked


class TestConfig:
    """Test cases for Config (Facade)"""

    def test_initialization_defaults(self, monkeypatch, tmp_path):
        """Test Config initialization with defaults"""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test123")

        # Create a temporary image folder
        image_folder = tmp_path / "images"
        image_folder.mkdir()
        (image_folder / "test.png").touch()

        config = Config(images_folder=image_folder)
        assert config.output_file == "extracted_data_gpt_all.csv"
        assert config.extract_fields == ["filename", "email", "firstname", "name"]

    def test_custom_extract_fields(self, monkeypatch, tmp_path):
        """Test Config with custom extract fields"""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test123")

        image_folder = tmp_path / "images"
        image_folder.mkdir()
        (image_folder / "test.png").touch()

        custom_fields = ["email", "name"]
        config = Config(images_folder=image_folder, extract_fields=custom_fields)
        assert config.extract_fields == custom_fields

    def test_validate_success(self, monkeypatch, tmp_path):
        """Test successful validation"""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test123")

        image_folder = tmp_path / "images"
        image_folder.mkdir()
        (image_folder / "test.png").touch()

        config = Config(images_folder=image_folder)
        config.validate()  # Should not raise

    def test_config_integration(self, monkeypatch, tmp_path):
        """Test Config integration with all sub-configs"""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test123")

        image_folder = tmp_path / "images"
        image_folder.mkdir()
        (image_folder / "test.png").touch()

        config = Config(images_folder=image_folder)

        # Check all sub-configs are accessible
        assert config.env is not None
        assert config.images is not None
        assert config.openai is not None
        assert config.openai.api_key == "sk-test123"
