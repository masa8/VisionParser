"""Main script to extract Email, Firstname, and Name from images"""

import logging
from openai import OpenAI

from models import Config
from models.env_config import EnvConfigError
from models.image_folder_config import ImageFolderConfigError
from models.openai_config import OpenAIConfigError
from services.extractor import ImageDataExtractor
from services.processor import DataProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    """Main processing function"""
    try:
        # Initialize configuration (extraction fields can be customized)
        config = Config(extract_fields=["filename", "email", "firstname", "name"])
        config.validate()

        logger.info("Configuration:")
        logger.info(str(config))
        logger.info(f"Extraction fields: {', '.join(config.extract_fields)}")

        # Initialize services
        client = OpenAI(api_key=config.openai.api_key)
        extractor = ImageDataExtractor(client, config)
        processor = DataProcessor(
            extractor=extractor,
            output_file=config.output_file,
            fields=config.extract_fields,
        )

        # Get image files
        image_files = config.images.get_image_files()

        logger.info(f"Processing {len(image_files)} images...")
        logger.warning("Note: Using GPT-4 Vision may take some time")

        # Process images
        result = processor.process_images(image_files, verbose=True)

        # Save results
        processor.save_to_csv(result.all_results)

        # Display summary
        processor.log_summary(result)

        return 0

    except (EnvConfigError, ImageFolderConfigError, OpenAIConfigError) as e:
        logger.error(f"Configuration error: {str(e)}")
        return 1

    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        return 1

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
