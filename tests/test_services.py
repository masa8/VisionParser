"""Tests for services package"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from services.extractor import (
    ImageDataExtractor,
    ImageProcessingError,
    OpenAIAPIError,
)
from services.processor import DataProcessor, ProcessingResult


class TestImageDataExtractor:
    """Test cases for ImageDataExtractor"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock OpenAI client"""
        return Mock()

    @pytest.fixture
    def mock_config(self):
        """Create a mock Config"""
        config = Mock()
        config.openai = Mock()
        config.openai.model = "gpt-4o"
        config.openai.max_tokens = 2000
        config.openai.temperature = 0.0
        return config

    @pytest.fixture
    def extractor(self, mock_client, mock_config):
        """Create an ImageDataExtractor instance"""
        return ImageDataExtractor(mock_client, mock_config)

    def test_initialization(self, mock_client, mock_config):
        """Test ImageDataExtractor initialization"""
        extractor = ImageDataExtractor(mock_client, mock_config)
        assert extractor.client == mock_client
        assert extractor.config == mock_config

    @patch("services.extractor.encode_image")
    def test_extract_all_info_success(
        self, mock_encode, extractor, mock_client, tmp_path
    ):
        """Test successful data extraction"""
        # Setup
        test_image = tmp_path / "test.png"
        test_image.touch()

        mock_encode.return_value = "base64_encoded_image"

        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """[
            {"email": "test@example.com", "firstname": "John", "name": "John Doe"}
        ]"""
        mock_client.chat.completions.create.return_value = mock_response

        # Execute
        results = extractor.extract_all_info(str(test_image))

        # Verify
        assert len(results) == 1
        assert results[0]["email"] == "test@example.com"
        assert results[0]["firstname"] == "John"
        assert results[0]["name"] == "John Doe"
        assert results[0]["filename"] == "test.png"

    @patch("services.extractor.encode_image")
    def test_extract_all_info_with_json_markers(
        self, mock_encode, extractor, mock_client, tmp_path
    ):
        """Test extraction with JSON code block markers"""
        test_image = tmp_path / "test.png"
        test_image.touch()

        mock_encode.return_value = "base64_encoded_image"

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """```json
[
    {"email": "test@example.com", "firstname": "Jane", "name": "Jane Smith"}
]
```"""
        mock_client.chat.completions.create.return_value = mock_response

        results = extractor.extract_all_info(str(test_image))

        assert len(results) == 1
        assert results[0]["email"] == "test@example.com"

    @patch("services.extractor.encode_image")
    def test_extract_all_info_json_decode_error(
        self, mock_encode, extractor, mock_client, tmp_path
    ):
        """Test handling of JSON decode error"""
        test_image = tmp_path / "test.png"
        test_image.touch()

        mock_encode.return_value = "base64_encoded_image"

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Invalid JSON"
        mock_client.chat.completions.create.return_value = mock_response

        with pytest.raises(OpenAIAPIError) as exc_info:
            extractor.extract_all_info(str(test_image))

        assert "JSON parse error" in str(exc_info.value)

    @patch("services.extractor.encode_image")
    def test_extract_all_info_general_error(
        self, mock_encode, extractor, mock_client, tmp_path
    ):
        """Test handling of general errors"""
        test_image = tmp_path / "test.png"
        test_image.touch()

        mock_encode.side_effect = Exception("File read error")

        with pytest.raises(ImageProcessingError) as exc_info:
            extractor.extract_all_info(str(test_image))

        assert test_image.name in str(exc_info.value)

    @patch("services.extractor.encode_image")
    def test_extract_all_info_empty_response(
        self, mock_encode, extractor, mock_client, tmp_path
    ):
        """Test extraction with empty response"""
        test_image = tmp_path / "test.png"
        test_image.touch()

        mock_encode.return_value = "base64_encoded_image"

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "[]"
        mock_client.chat.completions.create.return_value = mock_response

        results = extractor.extract_all_info(str(test_image))

        assert len(results) == 0


class TestProcessingResult:
    """Test cases for ProcessingResult"""

    def test_processing_result_success_rate(self):
        """Test success rate calculation"""
        result = ProcessingResult(
            total_images=10,
            successful_images=8,
            failed_images=["img1.png", "img2.png"],
            total_records=24,
            all_results=[],
        )
        assert result.success_rate == 80.0

    def test_processing_result_zero_images(self):
        """Test success rate with zero images"""
        result = ProcessingResult(
            total_images=0,
            successful_images=0,
            failed_images=[],
            total_records=0,
            all_results=[],
        )
        assert result.success_rate == 0.0


class TestDataProcessor:
    """Test cases for DataProcessor"""

    @pytest.fixture
    def mock_extractor(self):
        """Create a mock extractor"""
        return Mock()

    @pytest.fixture
    def processor(self, mock_extractor):
        """Create a DataProcessor instance"""
        return DataProcessor(
            extractor=mock_extractor,
            output_file="test_output.csv",
            fields=["filename", "email", "firstname", "name"],
        )

    def test_initialization(self, mock_extractor):
        """Test DataProcessor initialization"""
        processor = DataProcessor(
            extractor=mock_extractor,
            output_file="output.csv",
            fields=["email", "name"],
        )
        assert processor.extractor == mock_extractor
        assert processor.output_file == "output.csv"
        assert processor.fields == ["email", "name"]

    def test_process_images_success(self, processor, mock_extractor, tmp_path):
        """Test successful image processing"""
        # Create test files
        test_files = [tmp_path / "test1.png", tmp_path / "test2.png"]
        for f in test_files:
            f.touch()

        # Mock extraction results
        mock_extractor.extract_all_info.return_value = [
            {"email": "test@example.com", "firstname": "John", "name": "John Doe"}
        ]

        # Process images
        result = processor.process_images(test_files, verbose=False)

        # Verify
        assert result.total_images == 2
        assert result.successful_images == 2
        assert len(result.failed_images) == 0
        assert result.total_records == 2
        assert len(result.all_results) == 2

    def test_process_images_with_failures(self, processor, mock_extractor, tmp_path):
        """Test image processing with some failures"""
        test_files = [tmp_path / "test1.png", tmp_path / "test2.png"]
        for f in test_files:
            f.touch()

        # Mock: first succeeds, second fails
        mock_extractor.extract_all_info.side_effect = [
            [{"email": "test@example.com", "firstname": "John", "name": "John Doe"}],
            Exception("Processing error"),
        ]

        result = processor.process_images(test_files, verbose=False)

        assert result.total_images == 2
        assert result.successful_images == 1
        assert len(result.failed_images) == 1
        assert result.total_records == 1

    def test_process_images_empty_results(self, processor, mock_extractor, tmp_path):
        """Test processing with empty results"""
        test_files = [tmp_path / "test1.png"]
        test_files[0].touch()

        mock_extractor.extract_all_info.return_value = []

        result = processor.process_images(test_files, verbose=False)

        assert result.total_images == 1
        assert result.successful_images == 0
        assert len(result.failed_images) == 1

    def test_save_to_csv(self, processor, tmp_path):
        """Test saving results to CSV"""
        output_file = tmp_path / "output.csv"
        processor.output_file = str(output_file)

        test_results = [
            {
                "filename": "test.png",
                "email": "test@example.com",
                "firstname": "John",
                "name": "John Doe",
            }
        ]

        processor.save_to_csv(test_results)

        # Verify file was created and contains data
        assert output_file.exists()
        content = output_file.read_text()
        assert "filename,email,firstname,name" in content
        assert "test@example.com" in content

    def test_log_summary(self, processor, caplog):
        """Test logging summary"""
        import logging

        caplog.set_level(logging.INFO)

        result = ProcessingResult(
            total_images=5,
            successful_images=4,
            failed_images=["failed.png"],
            total_records=12,
            all_results=[],
        )

        processor.log_summary(result)

        # Check that logging occurred (caplog captures log messages)
        log_messages = [record.message for record in caplog.records]
        assert any("Complete!" in msg for msg in log_messages)
