"""Image processing utilities"""

import base64


def encode_image(image_path: str) -> str:
    """
    Encode image to base64

    Args:
        image_path: Path to image file

    Returns:
        Base64-encoded image string
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
