"""Image data extraction service"""

import json
from pathlib import Path
from typing import List, Dict
from openai import OpenAI

from models import Config
from utils.image_utils import encode_image


class ImageProcessingError(Exception):
    """Error during image processing"""

    def __init__(self, image_path: str, original_error: Exception):
        super().__init__(
            f"Error occurred while processing image: {image_path}\n"
            f"Error details: {str(original_error)}"
        )
        self.image_path = image_path
        self.original_error = original_error


class OpenAIAPIError(Exception):
    """Error during OpenAI API call"""

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error


class ImageDataExtractor:
    """Service class for extracting data from images"""

    def __init__(self, client: OpenAI, config: Config):
        """
        Initialize

        Args:
            client: OpenAI client
            config: Application configuration
        """
        self.client = client
        self.config = config

    def extract_all_info(self, image_path: str) -> List[Dict[str, str]]:
        """
        Extract all information from image using GPT-4 Vision

        Args:
            image_path: Path to the image file

        Returns:
            List of extracted data

        Raises:
            ImageProcessingError: Error during image processing
            OpenAIAPIError: Error during API call
        """
        try:
            base64_image = encode_image(image_path)

            response = self.client.chat.completions.create(
                model=self.config.openai.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """This image contains a table with three columns: Email, First name, and Name (Full name).

Please extract the following information from all rows in the table (excluding the header row):
1. Email (email address)
2. First name
3. Name (full name)

Return in the following JSON array format (JSON only, no explanation):
[
  {
    "email": "extracted email address 1",
    "firstname": "extracted first name 1",
    "name": "extracted full name 1"
  }
]

Extract all rows. If no data is found, return an empty array.""",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=self.config.openai.max_tokens,
                temperature=self.config.openai.temperature,
            )

            content = response.choices[0].message.content.strip()

            # Remove JSON markers
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            data_list = json.loads(content)

            # Format results
            results = []
            for data in data_list:
                results.append(
                    {
                        "filename": Path(image_path).name,
                        "email": data.get("email", ""),
                        "firstname": data.get("firstname", ""),
                        "name": data.get("name", ""),
                    }
                )

            return results

        except json.JSONDecodeError as e:
            raise OpenAIAPIError(f"JSON parse error: {image_path}", e)
        except Exception as e:
            raise ImageProcessingError(image_path, e)
