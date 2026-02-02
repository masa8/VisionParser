"""Tests for main module"""

from unittest.mock import Mock, patch
from pathlib import Path
import main


class TestMain:
    """Test cases for main function"""

    @patch("main.OpenAI")
    @patch("main.Config")
    @patch("main.ImageDataExtractor")
    @patch("main.DataProcessor")
    def test_main_success(
        self,
        mock_processor_class,
        mock_extractor_class,
        mock_config_class,
        mock_openai_class,
        tmp_path,
    ):
        """Test successful main execution"""
        # Setup mocks
        mock_config = Mock()
        mock_config.openai.api_key = "sk-test123"
        mock_config.extract_fields = ["filename", "email", "firstname", "name"]
        mock_config.output_file = "output.csv"

        # Mock image files
        mock_images = Mock()
        mock_images.get_image_files.return_value = [Path("test.png")]
        mock_config.images = mock_images

        mock_config_class.return_value = mock_config

        # Mock OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock extractor
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor

        # Mock processor
        mock_processor = Mock()
        from services.processor import ProcessingResult

        mock_result = ProcessingResult(
            total_images=1,
            successful_images=1,
            failed_images=[],
            total_records=3,
            all_results=[{"email": "test@example.com"}],
        )
        mock_processor.process_images.return_value = mock_result
        mock_processor_class.return_value = mock_processor

        # Execute
        result = main.main()

        # Verify
        assert result == 0
        mock_config.validate.assert_called_once()
        mock_processor.process_images.assert_called_once()
        mock_processor.save_to_csv.assert_called_once()
        mock_processor.log_summary.assert_called_once()

    @patch("main.Config")
    def test_main_config_error(self, mock_config_class):
        """Test main with configuration error"""
        from models.env_config import OpenAIKeyNotFoundError

        mock_config_class.side_effect = OpenAIKeyNotFoundError()

        result = main.main()

        assert result == 1

    @patch("main.OpenAI")
    @patch("main.Config")
    @patch("main.ImageDataExtractor")
    @patch("main.DataProcessor")
    def test_main_keyboard_interrupt(
        self,
        mock_processor_class,
        mock_extractor_class,
        mock_config_class,
        mock_openai_class,
    ):
        """Test main with keyboard interrupt"""
        # Setup mocks
        mock_config = Mock()
        mock_config.openai.api_key = "sk-test123"
        mock_config.extract_fields = ["filename", "email"]
        mock_config.output_file = "output.csv"

        mock_images = Mock()
        mock_images.get_image_files.return_value = [Path("test.png")]
        mock_config.images = mock_images

        mock_config_class.return_value = mock_config

        # Mock processor to raise KeyboardInterrupt
        mock_processor = Mock()
        mock_processor.process_images.side_effect = KeyboardInterrupt()
        mock_processor_class.return_value = mock_processor

        # Mock other components
        mock_openai_class.return_value = Mock()
        mock_extractor_class.return_value = Mock()

        result = main.main()

        assert result == 1

    @patch("main.OpenAI")
    @patch("main.Config")
    @patch("main.ImageDataExtractor")
    @patch("main.DataProcessor")
    def test_main_unexpected_error(
        self,
        mock_processor_class,
        mock_extractor_class,
        mock_config_class,
        mock_openai_class,
    ):
        """Test main with unexpected error"""
        # Setup mocks
        mock_config = Mock()
        mock_config.openai.api_key = "sk-test123"
        mock_config.extract_fields = ["filename", "email"]
        mock_config.output_file = "output.csv"

        mock_images = Mock()
        mock_images.get_image_files.return_value = [Path("test.png")]
        mock_config.images = mock_images

        mock_config_class.return_value = mock_config

        # Mock processor to raise unexpected exception
        mock_processor = Mock()
        mock_processor.process_images.side_effect = RuntimeError("Unexpected error")
        mock_processor_class.return_value = mock_processor

        # Mock other components
        mock_openai_class.return_value = Mock()
        mock_extractor_class.return_value = Mock()

        result = main.main()

        assert result == 1

    @patch("main.Config")
    def test_main_with_custom_fields(self, mock_config_class):
        """Test that Config is called with correct extract_fields"""
        from models.env_config import OpenAIKeyNotFoundError

        # Make Config raise an error to exit early
        mock_config_class.side_effect = OpenAIKeyNotFoundError()

        main.main()

        # Verify Config was called with extract_fields
        mock_config_class.assert_called_once_with(
            extract_fields=["filename", "email", "firstname", "name"]
        )
