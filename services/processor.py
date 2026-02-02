"""Data processing service"""

import csv
import logging
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Data class representing processing results"""

    total_images: int
    successful_images: int
    failed_images: List[str]
    total_records: int
    all_results: List[Dict[str, str]]

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_images == 0:
            return 0.0
        return (self.successful_images / self.total_images) * 100


class DataProcessor:
    """Service class for data processing"""

    def __init__(self, extractor, output_file: str, fields: List[str]):
        """
        Initialize

        Args:
            extractor: Extraction service (ImageDataExtractor)
            output_file: Output filename
            fields: List of fields to extract and output
        """
        self.extractor = extractor
        self.output_file = output_file
        self.fields = fields

    def process_images(
        self,
        image_files: List[Path],
        verbose: bool = True,
        progress_callback: Optional[callable] = None,
    ) -> ProcessingResult:
        """
        Process image files

        Args:
            image_files: List of image files to process
            verbose: Whether to display detailed progress
            progress_callback: Progress callback function

        Returns:
            ProcessingResult: Processing result
        """
        all_results = []
        total_records = 0
        failed_images = []

        for i, image_file in enumerate(image_files, 1):
            if verbose:
                logger.info(f"Processing ({i}/{len(image_files)}): {image_file.name}")

            try:
                records = self.extractor.extract_all_info(str(image_file))

                if records:
                    if verbose:
                        logger.info(f"  Extracted {len(records)} records")
                        self._log_sample_records(records)

                    all_results.extend(records)
                    total_records += len(records)
                else:
                    failed_images.append(image_file.name)
                    if verbose:
                        logger.warning("  No records found")

            except Exception as e:
                if verbose:
                    logger.error(f"  Error: {str(e)}")
                failed_images.append(image_file.name)

            # Progress callback
            if progress_callback:
                progress_callback(i, len(image_files), image_file.name)

        return ProcessingResult(
            total_images=len(image_files),
            successful_images=len(image_files) - len(failed_images),
            failed_images=failed_images,
            total_records=total_records,
            all_results=all_results,
        )

    def _log_sample_records(self, records: List[Dict[str, str]], max_display: int = 3):
        """Log sample records"""
        for j, record in enumerate(records[:max_display], 1):
            # Display first 2 fields
            display_fields = [record.get(field, "") for field in self.fields[:2]]
            logger.info(f"    {j}. {' - '.join(filter(None, display_fields))}")

        if len(records) > max_display:
            logger.info(f"    ... and {len(records) - max_display} more")

    def save_to_csv(self, results: List[Dict[str, str]]) -> None:
        """
        Save results to CSV file

        Args:
            results: Result data to save
        """
        with open(self.output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fields)
            writer.writeheader()
            for result in results:
                writer.writerow(result)

    def log_summary(self, result: ProcessingResult) -> None:
        """
        Log processing summary

        Args:
            result: Processing result
        """
        logger.info(f"Complete! Data saved to {self.output_file}")
        logger.info("Results Summary:")
        logger.info(f"  - Images: {result.total_images}")
        logger.info(f"  - Successful: {result.successful_images}")
        logger.info(f"  - Failed: {len(result.failed_images)}")
        logger.info(f"  - Success rate: {result.success_rate:.1f}%")
        logger.info(f"  - Total records: {result.total_records}")

        if result.failed_images:
            logger.warning("Failed images:")
            for img in result.failed_images:
                logger.warning(f"  - {img}")
