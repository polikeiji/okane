"""Crawl subcommand implementation."""

import argparse
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from okane.lib.ai_analyzer import AIAnalyzer
from okane.lib.logging_config import configure_logging
from okane.models.config import WebsiteConfigurationList
from okane.services.crawler import Crawler
from okane.services.downloader import PDFDownloader
from okane.services.scraper import WebsiteScraper
from okane.services.storage import LocalStorageBackend


def setup_crawl_parser(subparsers: Any) -> None:
    """Setup crawl subcommand parser.

    Args:
        subparsers: Subparsers object from argparse
    """
    parser = subparsers.add_parser("crawl", help="Crawl government websites for PDFs")

    # Required arguments
    parser.add_argument(
        "--output-folder",
        "-o",
        required=True,
        help="Output folder (local path or Azure ADLS Gen2 path)",
    )

    # Optional arguments
    parser.add_argument(
        "--config",
        "-c",
        help="Custom website configuration JSON file (default: use built-in config)",
    )

    parser.add_argument(
        "--parallelism",
        "-p",
        type=int,
        default=1,
        help="Number of websites to crawl in parallel (default: 1)",
    )

    parser.add_argument(
        "--max-files",
        "-m",
        type=int,
        help="Maximum total PDFs to download (default: unlimited)",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    parser.add_argument(
        "--log-format",
        choices=["text", "json"],
        default="text",
        help="Log output format (default: text)",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP request timeout in seconds (default: 30)",
    )

    parser.add_argument(
        "--user-agent",
        default="Okane-Crawler/1.0.0 (+https://github.com/polikeiji/okane)",
        help="Custom User-Agent header",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate crawl without downloading files",
    )


def handle_crawl(args: argparse.Namespace) -> int:
    """Handle crawl subcommand.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0=success, 1=partial, 2=failure, 3=invalid args, 4=auth error, 5=permission error)
    """
    # Configure logging
    log_level = "DEBUG" if args.verbose >= 2 else args.log_level
    if args.quiet:
        log_level = "ERROR"

    logger = configure_logging(log_level, args.log_format, "okane")

    try:
        # Validate arguments
        exit_code = validate_arguments(args, logger)
        if exit_code != 0:
            return exit_code

        # Load configuration
        config = load_configuration(args.config, logger)
        if not config:
            return 3

        # Validate OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            return 4

        # Validate output folder
        storage = setup_storage(args.output_folder, logger)
        if not storage:
            return 5

        # Run crawl
        logger.info("Starting crawl...")
        logger.info(f"Configuration: {args.config or 'default (built-in)'}")
        logger.info(f"Output folder: {args.output_folder}")
        logger.info(f"Parallelism: {args.parallelism}")
        if args.max_files:
            logger.info(f"Max files: {args.max_files}")
        if args.dry_run:
            logger.info("DRY RUN MODE - No files will be downloaded")

        # Create services
        ai_analyzer = AIAnalyzer(api_key)
        scraper = WebsiteScraper(ai_analyzer, args.user_agent, args.timeout)
        downloader = PDFDownloader(args.user_agent, 300)
        crawler = Crawler(storage, scraper, downloader, logger)

        # Create initial metadata
        crawl_id = str(uuid.uuid4())
        crawl_start_time = datetime.now(timezone.utc)
        metadata = crawler.create_metadata(
            crawl_id=crawl_id,
            crawl_start_time=crawl_start_time,
            total_websites=len(config.websites),
            parallelism=args.parallelism,
            max_files_limit=args.max_files,
            output_folder=args.output_folder,
            storage_backend="local",  # TODO: detect from path
            config_file_path=args.config or "default",
        )

        # Crawl websites sequentially (parallelism will be added later)
        total_files_downloaded = 0
        for idx, website in enumerate(config.websites, 1):
            if not website.enabled:
                continue

            logger.info(f"[{idx}/{len(config.websites)}] Crawling: {website.name}")

            # Calculate remaining files
            max_files_remaining = None
            if args.max_files:
                max_files_remaining = args.max_files - total_files_downloaded
                if max_files_remaining <= 0:
                    logger.info("Reached max files limit")
                    break

            # Crawl website
            if not args.dry_run:
                downloaded_files, errors = crawler.crawl_website(website, max_files_remaining)

                # Update metadata
                metadata = crawler.update_metadata(
                    metadata, downloaded_files, errors, success=len(downloaded_files) > 0
                )

                # Save metadata after each website
                crawler.save_metadata(metadata)

                total_files_downloaded = metadata.total_pdfs_downloaded

                logger.info(
                    f"  PDFs downloaded: {len([f for f in downloaded_files if f.crawl_status == 'success'])}"
                )
            else:
                # Dry run - just analyze
                try:
                    pdf_urls, strategy = scraper.scrape_website(
                        website.id, str(website.base_url), max_files_remaining
                    )
                    logger.info(
                        f"  Found {len(pdf_urls)} PDF links (confidence: {strategy.confidence:.2f})"
                    )
                except Exception as e:
                    logger.error(f"  Error analyzing website: {e}")

        # Finalize metadata
        if not args.dry_run:
            metadata = crawler.finalize_metadata(metadata)
            crawler.save_metadata(metadata)

        # Print summary
        print_summary(metadata, args.log_format, logger)

        # Determine exit code
        if args.dry_run:
            return 0
        elif metadata.websites_failed == 0:
            return 0  # Complete success
        elif metadata.websites_crawled > 0:
            return 1  # Partial success
        else:
            return 2  # Complete failure

    except KeyboardInterrupt:
        logger.warning("Crawl interrupted by user")
        return 2
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 2


def validate_arguments(args: argparse.Namespace, logger: logging.Logger) -> int:
    """Validate command-line arguments.

    Args:
        args: Parsed arguments
        logger: Logger instance

    Returns:
        Exit code (0=valid, 3=invalid)
    """
    # Validate parallelism
    if args.parallelism <= 0:
        logger.error("Parallelism must be a positive integer")
        return 3

    # Validate max-files
    if args.max_files is not None and args.max_files <= 0:
        logger.error("Max files must be a positive integer")
        return 3

    return 0


def load_configuration(
    config_path: Optional[str], logger: logging.Logger
) -> Optional[WebsiteConfigurationList]:
    """Load website configuration.

    Args:
        config_path: Path to config file (None for default)
        logger: Logger instance

    Returns:
        WebsiteConfigurationList or None if load fails
    """
    try:
        if config_path:
            # Load custom configuration
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            return WebsiteConfigurationList(**config_data)
        else:
            # Load default configuration
            default_config_path = Path(__file__).parent.parent.parent.parent / "config" / "default_websites.json"
            with open(default_config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            return WebsiteConfigurationList(**config_data)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return None


def setup_storage(
    output_folder: str, logger: logging.Logger
) -> Optional[LocalStorageBackend]:
    """Setup storage backend.

    Args:
        output_folder: Output folder path
        logger: Logger instance

    Returns:
        Storage backend or None if setup fails
    """
    try:
        # For now, only support local storage
        # TODO: Add Azure ADLS Gen2 detection
        storage = LocalStorageBackend(output_folder)

        # Test write permission
        test_path = Path(output_folder) / ".okane_test"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.write_text("test")
        test_path.unlink()

        return storage
    except PermissionError:
        logger.error(f"Output folder not writable: {output_folder}")
        return None
    except Exception as e:
        logger.error(f"Error setting up storage: {e}")
        return None


def print_summary(
    metadata: Any, log_format: str, logger: logging.Logger
) -> None:
    """Print crawl summary.

    Args:
        metadata: CrawlMetadata object
        log_format: Output format (text or json)
        logger: Logger instance
    """
    if log_format == "json":
        # JSON summary
        summary = {
            "status": "success"
            if metadata.websites_failed == 0
            else "partial_success"
            if metadata.websites_crawled > 0
            else "failure",
            "summary": {
                "total_websites": metadata.total_websites,
                "websites_crawled": metadata.websites_crawled,
                "websites_failed": metadata.websites_failed,
                "total_pdfs_downloaded": metadata.total_pdfs_downloaded,
                "total_pdfs_failed": metadata.total_pdfs_failed,
                "total_bytes": metadata.total_bytes_downloaded,
                "output_folder": metadata.output_folder,
            },
        }
        print(json.dumps(summary, indent=2))
    else:
        # Text summary
        duration = (
            (metadata.crawl_end_time - metadata.crawl_start_time).total_seconds()
            if metadata.crawl_end_time
            else 0
        )
        print("\n" + "=" * 60)
        print("Crawl Summary:")
        print(f"  Websites crawled: {metadata.websites_crawled}/{metadata.total_websites}")
        if metadata.websites_failed > 0:
            print(f"  Websites failed: {metadata.websites_failed}")
        print(f"  PDFs downloaded: {metadata.total_pdfs_downloaded}")
        if metadata.total_pdfs_failed > 0:
            print(f"  PDFs failed: {metadata.total_pdfs_failed}")
        print(
            f"  Total size: {metadata.total_bytes_downloaded / (1024 * 1024):.1f} MB"
        )
        print(f"  Duration: {duration:.1f}s")
        print(f"\nMetadata saved to: {metadata.output_folder}/metadata.json")
        print("=" * 60)
