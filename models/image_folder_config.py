"""Image folder management class"""

from pathlib import Path
from typing import List


class ImageFolderConfigError(Exception):
    """Base class for image folder configuration errors"""

    pass


class ImageFolderNotFoundError(ImageFolderConfigError):
    """Image folder not found"""

    def __init__(self, folder_path: str):
        super().__init__(
            f"Image folder not found: {folder_path}\n"
            f"Please create the images folder and place image files in it."
        )


class NoImageFilesError(ImageFolderConfigError):
    """No image files found"""

    def __init__(self, folder_path: str):
        super().__init__(
            f"No image files found: {folder_path}\n"
            f"Supported formats: .png, .jpg, .jpeg, .bmp, .tiff"
        )


class ImageFolderConfig:
    """Class for managing image folder"""

    # Supported image extensions
    SUPPORTED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]

    def __init__(self, folder_path: str | Path = "images"):
        """
        Initialize image folder configuration

        Args:
            folder_path: Path to image folder (default: images)
        """
        self._folder_path = Path(folder_path)

    @property
    def folder_path(self) -> Path:
        """Get image folder path"""
        return self._folder_path

    @folder_path.setter
    def folder_path(self, value: str | Path) -> None:
        """Set image folder path"""
        self._folder_path = Path(value)

    def validate(self) -> None:
        """
        Validate existence of image folder

        Raises:
            ImageFolderNotFoundError: Image folder not found
        """
        if not self._folder_path.exists():
            raise ImageFolderNotFoundError(str(self._folder_path))

    def get_image_files(self) -> List[Path]:
        """
        Get image files from image folder

        Returns:
            List of image files

        Raises:
            ImageFolderNotFoundError: Image folder not found
            NoImageFilesError: No image files found
        """
        # Check folder existence
        self.validate()

        # Get image files
        image_files = sorted(
            [
                f
                for f in self._folder_path.iterdir()
                if f.suffix.lower() in self.SUPPORTED_EXTENSIONS
            ]
        )

        if not image_files:
            raise NoImageFilesError(str(self._folder_path))

        return image_files

    def __repr__(self) -> str:
        """String representation of configuration"""
        return f"ImageFolderConfig(folder_path={self._folder_path})"
