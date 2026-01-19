"""Core crawler orchestrator service."""

import json
import logging
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from okane.models.config import WebsiteConfiguration
from okane.models.metadata import CrawlMetadata, DownloadedPDF
from okane.services.downloader import PDFDownloader
from okane.services.scraper import WebsiteScraper
from okane.services.storage import StorageBackend


class Crawler:
    """Orchestrates the crawling process for government websites."""

    def __init__(
        self,
        storage: StorageBackend,
        scraper: WebsiteScraper,
        downloader: PDFDownloader,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """Initialize crawler.

        Args:
            storage: Storage backend for saving files
            scraper: Website scraper
            downloader: PDF downloader
            logger: Logger instance (optional)
        """
        self.storage = storage
        self.scraper = scraper
        self.downloader = downloader
        self.logger = logger or logging.getLogger("okane")

    def crawl_website(
        self,
        website: WebsiteConfiguration,
        max_files_remaining: Optional[int] = None,
    ) -> tuple[list[DownloadedPDF], list[dict[str, Any]]]:
        """Crawl a single website and download PDFs.

        Args:
            website: Website configuration
            max_files_remaining: Maximum number of files to download (None for unlimited)

        Returns:
            Tuple of (list of downloaded PDFs metadata, list of errors)
        """
        downloaded_files: list[DownloadedPDF] = []
        errors: list[dict[str, Any]] = []

        if not website.enabled:
            self.logger.info(f"Skipping disabled website: {website.name}")
            return downloaded_files, errors

        self.logger.info(f"Crawling website: {website.name} ({website.id})")

        try:
            # Scrape website to get PDF URLs
            self.logger.debug(f"Analyzing website structure: {website.base_url}")
            pdf_urls, strategy = self.scraper.scrape_website(
                website.id, str(website.base_url), max_files_remaining
            )

            self.logger.info(
                f"Found {len(pdf_urls)} PDF links (confidence: {strategy.confidence:.2f})"
            )

            # Download each PDF
            for idx, pdf_url in enumerate(pdf_urls, 1):
                if max_files_remaining is not None and len(downloaded_files) >= max_files_remaining:
                    self.logger.info(f"Reached max files limit for website: {website.id}")
                    break

                self.logger.debug(f"Downloading PDF {idx}/{len(pdf_urls)}: {pdf_url}")

                try:
                    # Download PDF
                    content, metadata, error = self.downloader.download_pdf_with_retry(
                        pdf_url, website.id, website.id
                    )

                    if content and metadata and not error:
                        # Save to storage
                        self.storage.write_file(content, metadata.local_path)
                        downloaded_files.append(metadata)
                        self.logger.debug(
                            f"Successfully downloaded: {metadata.filename} "
                            f"({metadata.file_size_bytes} bytes)"
                        )
                    else:
                        # Download failed
                        if metadata:
                            downloaded_files.append(metadata)
                        errors.append(
                            {
                                "website_id": website.id,
                                "url": pdf_url,
                                "error_type": "DownloadError",
                                "error_message": error or "Unknown error",
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            }
                        )
                        self.logger.warning(f"Failed to download PDF: {pdf_url} - {error}")

                except Exception as e:
                    # Unexpected error during download
                    errors.append(
                        {
                            "website_id": website.id,
                            "url": pdf_url,
                            "error_type": type(e).__name__,
                            "error_message": str(e),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )
                    self.logger.error(f"Error downloading PDF: {pdf_url} - {e}")

        except Exception as e:
            # Website-level error (scraping failed)
            errors.append(
                {
                    "website_id": website.id,
                    "url": str(website.base_url),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            self.logger.error(f"Failed to crawl website {website.name}: {e}")

        return downloaded_files, errors

    def save_metadata(self, metadata: CrawlMetadata) -> None:
        """Save crawl metadata to storage atomically.

        Args:
            metadata: Crawl metadata to save

        Raises:
            IOError: If save operation fails
        """
        # Serialize metadata to JSON
        metadata_json = metadata.model_dump_json(indent=2)

        # Write to storage atomically
        self.storage.write_file(metadata_json.encode("utf-8"), "metadata.json")
        self.logger.debug("Saved metadata to storage")

    def create_metadata(
        self,
        crawl_id: str,
        crawl_start_time: datetime,
        total_websites: int,
        parallelism: int,
        max_files_limit: Optional[int],
        output_folder: str,
        storage_backend: str,
        config_file_path: str,
    ) -> CrawlMetadata:
        """Create initial crawl metadata.

        Args:
            crawl_id: Unique crawl identifier
            crawl_start_time: When the crawl started
            total_websites: Total number of websites to crawl
            parallelism: Parallelism level
            max_files_limit: Max files limit (None for unlimited)
            output_folder: Output folder path
            storage_backend: Storage backend type
            config_file_path: Path to config file

        Returns:
            Initial CrawlMetadata object
        """
        return CrawlMetadata(
            crawl_id=crawl_id,
            crawl_start_time=crawl_start_time,
            crawl_end_time=None,
            total_websites=total_websites,
            websites_crawled=0,
            websites_failed=0,
            total_pdfs_discovered=0,
            total_pdfs_downloaded=0,
            total_pdfs_failed=0,
            total_bytes_downloaded=0,
            parallelism=parallelism,
            max_files_limit=max_files_limit,
            output_folder=output_folder,
            storage_backend=storage_backend,
            config_file_path=config_file_path,
            downloaded_files=[],
            errors=[],
            metadata_version="1.0",
        )

    def update_metadata(
        self,
        metadata: CrawlMetadata,
        downloaded_files: list[DownloadedPDF],
        errors: list[dict[str, Any]],
        success: bool,
    ) -> CrawlMetadata:
        """Update metadata with crawl results.

        Args:
            metadata: Current metadata
            downloaded_files: List of downloaded files to add
            errors: List of errors to add
            success: Whether the website crawl was successful

        Returns:
            Updated CrawlMetadata object
        """
        # Add downloaded files
        metadata.downloaded_files.extend(downloaded_files)

        # Add errors
        metadata.errors.extend(errors)

        # Update counters
        successful_downloads = [f for f in downloaded_files if f.crawl_status == "success"]
        failed_downloads = [f for f in downloaded_files if f.crawl_status == "failed"]

        metadata.total_pdfs_discovered += len(downloaded_files)
        metadata.total_pdfs_downloaded += len(successful_downloads)
        metadata.total_pdfs_failed += len(failed_downloads)
        metadata.total_bytes_downloaded += sum(f.file_size_bytes for f in successful_downloads)

        if success and downloaded_files:
            metadata.websites_crawled += 1
        elif not success or errors:
            metadata.websites_failed += 1

        return metadata

    def finalize_metadata(self, metadata: CrawlMetadata) -> CrawlMetadata:
        """Finalize metadata with end time.

        Args:
            metadata: Metadata to finalize

        Returns:
            Finalized CrawlMetadata object
        """
        metadata.crawl_end_time = datetime.now(timezone.utc)
        return metadata
