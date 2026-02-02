"""Tests for utils package"""

import pytest
import base64
from utils.image_utils import encode_image


class TestImageUtils:
    """Test cases for image utilities"""

    def test_encode_image_png(self, tmp_path):
        """Test encoding a PNG image"""
        # Create a simple test image file
        test_image = tmp_path / "test.png"
        test_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        test_image.write_bytes(test_data)

        # Encode the image
        encoded = encode_image(str(test_image))

        # Verify it's a valid base64 string
        assert isinstance(encoded, str)
        decoded = base64.b64decode(encoded)
        assert decoded == test_data

    def test_encode_image_jpg(self, tmp_path):
        """Test encoding a JPG image"""
        test_image = tmp_path / "test.jpg"
        test_data = b"\xff\xd8\xff\xe0\x00\x10JFIF"
        test_image.write_bytes(test_data)

        encoded = encode_image(str(test_image))

        assert isinstance(encoded, str)
        decoded = base64.b64decode(encoded)
        assert decoded == test_data

    def test_encode_image_file_not_found(self):
        """Test encoding non-existent file"""
        with pytest.raises(FileNotFoundError):
            encode_image("/nonexistent/path/image.png")

    def test_encode_image_returns_string(self, tmp_path):
        """Test that encode_image returns a string"""
        test_image = tmp_path / "test.png"
        test_image.write_bytes(b"fake image data")

        result = encode_image(str(test_image))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_encode_empty_file(self, tmp_path):
        """Test encoding an empty file"""
        test_image = tmp_path / "empty.png"
        test_image.touch()

        encoded = encode_image(str(test_image))
        assert encoded == ""  # Empty file should encode to empty string
